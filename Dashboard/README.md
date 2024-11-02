# Mobility Data Dashboard
Interactive dashboard for visualizing and analyzing mobility data.

## Directory Structure
Dashboard/
├── data/
│   ├── trips/
│   ├── shapes/
│   └── population/
├── src/
│   ├── preprocess.py
│   └── dashboard.py
├── Dockerfile
├── requirements.txt
└── README.md

### Using Docker (Recommended)
1. Build: `docker build -t national-mobility-dashboard .`
2. Run: `docker run -p 8050:8050 -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs national-mobility-dashboard`
3. Access: http://localhost:8050

### Manual Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Place data files in their respective directories under `data/`
3. Run preprocessing: `python src/preprocess.py`
4. Start dashboard: `python src/dashboard.py`

## Required Data Files
Place these files in the appropriate data subdirectories:
- trips/AvgDayHourlyTrips201819_1270_weekday_v1.csv
- trips/AvgDayHourlyTrips201819_1270_weekday_arrival_v1.2.csv
- shapes/1270_02.09.2021.shp
- shapes/1270_02.09.2021.shx
- shapes/1270_02.09.2021.dbf
- shapes/1270_02.09.2021.prj
- population/1270_population.xlsx

## Logs

Logs are stored in the logs directory. When running with Docker, you can access them using:

'docker cp <container_id>:/app/logs ./logs'

