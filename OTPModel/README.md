# OTP Model Scripts

This folder contains scripts designed to calculate travel times by auto or public transit from any TAZ (Traffic Analysis Zone) to a focus TAZ, with the current setup focusing on Beer Sheva. These scripts can be modified to calculate travel times to any TAZ in Israel.

## Scripts

- **Clean-Israel-GTFS.py**: Prepares and cleans GTFS data for further processing in the OTP (OpenTripPlanner) model.
- **TravelTimes.py**: Calculates travel times by auto or public transit from specified TAZs to the focus TAZ.

## Prerequisite Data and Model Sources 

To use these scripts, you'll need to download the following:

- OTP Model: Download the latest version from [OTP Version Releases](https://github.com/opentripplanner/OpenTripPlanner/releases)
- GTFS Dataset: Obtain the current General Transit Feed Specification dataset from the [Ministry of Transport Portal](https://gtfs.mot.gov.il/gtfsfiles/)
- OSM Data: Download Open Street Map data for Israel and Palestine from [Geofabrik](https://download.geofabrik.de/asia/israel-and-palestine.html)
- TAZ Shapes: The TAZ (Traffic Analysis Zone) shape files are sourced from the main National Mobility Data folder. Ensure you have access to these files before running the scripts.