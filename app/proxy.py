import asyncio
import aiohttp
import statistics
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
from aiohttp import ClientTimeout
import time
import os

# InfluxDB configuration from environment variables
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN_FILE = os.getenv('INFLUXDB_TOKEN_FILE')
if INFLUXDB_TOKEN_FILE and os.path.exists(INFLUXDB_TOKEN_FILE):
    with open(INFLUXDB_TOKEN_FILE, 'r') as f:
        INFLUXDB_TOKEN = f.read().strip()
else:
    INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')

INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'aviation')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'flights')

# OpenSky Network API
OPENSKY_API_URL = os.getenv('OPENSKY_API_URL', 'https://opensky-network.org/api/states/all')

DAILY_LIMIT = 100  # 400 credits per day, 4 credits per request = 100 requests
REQUEST_INTERVAL = 400 
REQUEST_TIMEOUT = 30 

class FlightDataCollector:
    def __init__(self):
        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.last_request_time = 0
        self.requests_today = 0
        self.day_start = time.time() // 86400 * 86400 

    async def fetch_flight_data(self):
        await self.wait_for_next_slot()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(OPENSKY_API_URL, timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                    if response.status == 200:
                        self.last_request_time = time.time()
                        self.requests_today += 1
                        logging.info(f"Request successful. Total requests today: {self.requests_today}")
                        return await response.json()
                    elif response.status == 429:
                        logging.error("Rate limit exceeded, waiting for next slot")
                        await asyncio.sleep(REQUEST_INTERVAL)
                        return None
                    else:
                        logging.error(f"Error fetching data: {response.status}")
                        return None
        except Exception as e:
            logging.error(f"Exception during request: {str(e)}")
            return None

    def process_and_store_data(self, data):
        if not data or 'states' not in data:
            return

        try:
            current_time = datetime.now(timezone.utc)
            points = []

            total_flights = len(data['states'])
            if total_flights == 0:
                logging.warning("No flight data received")
                return

            altitudes = [state[7] for state in data['states'] if state[7] is not None]
            velocities = [state[9] for state in data['states'] if state[9] is not None]
            
            countries = {}
            for state in data['states']:
                origin = state[2] or 'Unknown'
                countries[origin] = countries.get(origin, 0) + 1

            stats_point = Point("flight_stats")\
                .field("total_flights", total_flights)
            
            if altitudes:
                stats_point.field("avg_altitude", statistics.mean(altitudes))\
                          .field("max_altitude", max(altitudes))
            
            if velocities:
                stats_point.field("avg_velocity", statistics.mean(velocities))\
                          .field("max_velocity", max(velocities))
            
            points.append(stats_point.time(current_time))

            # Country specific data
            for country, count in countries.items():
                points.append(
                    Point("country_stats")
                    .tag("country", country)
                    .field("flight_count", count)
                    .time(current_time)
                )

            if altitudes:
                min_alt = min(altitudes)
                max_alt = max(altitudes)
                bin_size = (max_alt - min_alt) / 10 if max_alt > min_alt else 1
                
                bins = {}
                for alt in altitudes:
                    bin_idx = int((alt - min_alt) / bin_size)
                    if bin_idx == 10:
                        bin_idx = 9
                    bin_key = f"{min_alt + bin_idx * bin_size:.0f}-{min_alt + (bin_idx + 1) * bin_size:.0f}"
                    bins[bin_key] = bins.get(bin_key, 0) + 1

                for bin_key, count in bins.items():
                    points.append(
                        Point("altitude_distribution")
                        .tag("bin", bin_key)
                        .field("count", count)
                        .time(current_time)
                    )

            for state in data['states']:
                if not all([state[0], state[5], state[6]]):
                    continue

                flight_point = Point("flights")\
                    .tag("icao24", state[0])\
                    .tag("origin_country", state[2] or "Unknown")

                if state[5] is not None:
                    flight_point.field("longitude", float(state[5]))
                if state[6] is not None:
                    flight_point.field("latitude", float(state[6]))
                if state[7] is not None:
                    flight_point.field("altitude", float(state[7]))
                if state[9] is not None:
                    flight_point.field("velocity", float(state[9]))
                if state[11] is not None: 
                    flight_point.field("vertical_rate", float(state[11]))
                if state[8] is not None: 
                    flight_point.field("on_ground", bool(state[8]))
                
                points.append(flight_point.time(current_time))

            try:
                self.write_api.write(bucket=INFLUXDB_BUCKET, record=points)
                logging.info(f"Successfully stored data for {total_flights} flights at {current_time}")
            except Exception as e:
                logging.error(f"Error writing to InfluxDB: {str(e)}")
                
        except Exception as e:
            logging.error(f"Error processing data: {str(e)}")

    async def cleanup(self):
        if self.client:
            self.client.close()

async def main():
    collector = FlightDataCollector()
    
    try:
        while True:
            try:
                data = await collector.fetch_flight_data()
                if data:
                    collector.process_and_store_data(data)
                else:
                    logging.warning("No data received")
                
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
            
            await asyncio.sleep(REQUEST_INTERVAL)
            
    except KeyboardInterrupt:
        logging.info("Collector stopped by user")
    finally:
        await collector.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Collector stopped by user")