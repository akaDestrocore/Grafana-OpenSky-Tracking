# OpenSky Network Aviation Tracker

![Grafana Dashboard](https://img.shields.io/badge/Grafana-Dashboard-orange)
![InfluxDB](https://img.shields.io/badge/Database-InfluxDB-blue)
![Python](https://img.shields.io/badge/Language-Python-green)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)

## ⚡ One-Command Installation

If you have Docker and Docker Compose installed, just run:
```bash
docker-compose up
```
That's it! You'll have a complete aviation tracking system running on your machine in minutes.

A real-time aviation tracking system that combines the power of OpenSky Network's flight data with modern DevOps practices and data visualization technologies. This project demonstrates advanced data engineering capabilities by seamlessly integrating multiple technologies into a cohesive, easy-to-deploy solution.

## 🌟 Key Features

- **Real-time Flight Tracking**: Continuous monitoring of global aviation traffic through OpenSky Network's API
- **Advanced Data Processing**: Efficient handling of complex flight data with automated parsing and storage
- **Interactive Dashboards**: 
  - Country-specific aviation statistics with geospatial visualization
  - Individual aircraft tracking with detailed flight metrics
  - Real-time statistics including altitude, velocity, and vertical rate
- **Robust Data Storage**: Time-series data management using InfluxDB 2.0
- **Containerized Architecture**: Fully dockerized setup for consistent deployment
- **Simplified Deployment**: Single-command deployment using Docker Compose

## 🛠️ Technical Stack

- **Data Collection**: Python with asyncio for efficient API polling
- **Database**: InfluxDB 2.0 for time-series data storage
- **Visualization**: Grafana with custom dashboards
- **Deployment**: Docker and Docker Compose
- **Development**: Modern Python practices with environment variable configuration

## 📊 Available Dashboards

### 1. Real-Time Stats by Country
- Interactive world map with flight positions
- Current flight count per country
- Airport congestion metrics
- Top 5 countries by active flights
- Distribution of airborne vs. grounded aircraft

### 2. Track Plane Stats
- Individual aircraft tracking
- Real-time altitude monitoring
- Current velocity measurements
- Vertical rate analysis
- Historical flight path visualization

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on your machine

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/yourusername/opensky-tracker.git
cd opensky-tracker
```

2. Start the containers:
```bash
docker-compose up
```

That's all! No additional configuration needed. The containers will start automatically with the proper configuration.

Access your dashboards at `http://localhost:3000`
- Default username: `admin`
- Default password: `admin`

## 🏗️ Architecture

The project follows a modern microservices architecture:

1. **Data Collection Service** (`proxy.py`):
   - Implements rate limiting for API compliance
   - Processes and transforms raw flight data
   - Uses asyncio for non-blocking operations

2. **Database Layer** (InfluxDB):
   - Optimized for time-series data
   - Efficient data compression
   - Built-in data retention policies
   - Secure token-based authentication

3. **Visualization Layer** (Grafana):
   - Custom-designed dashboards
   - Real-time data updates
   - Interactive filtering and exploration
   - Responsive design for various screen sizes

## 💡 Technical Highlights

This project showcases several advanced software engineering practices:

- **Efficient Data Collection**: Implements smart rate limiting to maintain API compliance while maximizing data collection
- **Scalable Architecture**: Containerized services can be easily scaled or modified
- **Security First**: Secure credentials management using Docker secrets
- **Infrastructure as Code**: Complete environment defined in Docker Compose
- **Single Command Deployment**: Simple setup process requiring minimal configuration