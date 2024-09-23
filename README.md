# Mobility Scripts
Scripts for analyzing Israel National Transport Behavior based on aggregated cellular data collected during 2018-2019.
## Scripts
- `hh-maps.py`: Creates maps of trip data to inputted TAZs on a half-hour level.
- `total-map.py`: Creates maps of trip data to inputted TAZs, summing all trips for the day.
- `TAZ-Comparisons.py`: Computes comparisons between TAZs.
- `IL-Merge-Census-TAZ.py`: Links TAZs to census statistical zones through intersections.
## Data Source
- Data is sourced from [Israel Government Data Portal](https://data.gov.il/dataset/tripscelular_1819).


### OTP Model

The scripts in the `OTPModel` folder are designed to calculate travel times by auto or public transit from any TAZ to a focus TAZ, with the current setup focusing on Beer Sheva. These scripts can be modified to calculate travel times to any TAZ in Israel.

- **Clean-Israel-GTFS.py**: Prepares and cleans GTFS data for further processing in the OTP (OpenTripPlanner) model.
- **TravelTimes.py**: Calculates travel times by auto or public transit from specified TAZs to the focus TAZ.

# Prerequisite Data and Model Sources 
- The OTP Model version can be downloaded at [OTP Version Releases](https://github.com/opentripplanner/OpenTripPlanner/releases)
- Current GTFS (General Transit Feed Specification) Dataset can be downloaded at the [Ministry of Transport Portal](https://gtfs.mot.gov.il/gtfsfiles/)
- OSM (Open Street Map) data can be downloaded on [geofabrik downloads](https://download.geofabrik.de/asia/israel-and-palestine.html)
