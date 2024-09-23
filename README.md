# National Mobility Data Analysis Scripts

This folder contains scripts and tools for analyzing Israel's National Transport Behavior based on aggregated cellular data collected during 2018-2019.

## Main Scripts

- `hh-maps.py`: Creates maps of trip data to inputted TAZs on a half-hour level.
- `total-map.py`: Creates maps of trip data to inputted TAZs, summing all trips for the day.
- `TAZ-Comparisons.py`: Computes comparisons between TAZs.
- `IL-Merge-Census-TAZ.py`: Links TAZs to census statistical zones through intersections.

## Dashboard

The `Dashboard` folder contains scripts for creating an interactive dashboard to visualize the mobility data. Key files include:

- `validation-dash.py`: Validates the preprocessed data.
- `TAZ-dash.py`: Creates an interactive Dash application for visualizing TAZ (Traffic Analysis Zone) data.
- `preprocess-dash.py`: Preprocesses the raw data for use in the dashboard.
- `inspect.py`: Provides detailed inspection of the preprocessed data.

## ArcMap

The `ArcMap` folder contains scripts for generating data compatible with Kepler.gl for advanced geospatial visualization:

- `Kepler-preprocess.py`: Preprocesses data for Kepler.gl visualization.
- `Kepler-preprocess-mixed.py`: Preprocesses data with mixed granularity for Kepler.gl.
- `Kepler-combined-preprocessing.py`: Combines preprocessing steps for Kepler.gl data.

## OTP Model

The `OTPModel` folder contains scripts for calculating travel times using OpenTripPlanner:

- `Clean-Israel-GTFS.py`: Prepares and cleans GTFS data for the OTP model.
- `TravelTimes.py`: Calculates travel times by auto or public transit between TAZs.

Note: The OTP Model uses TAZ shape files from the main data source in this folder.

## Data Source

- Main data is sourced from [Israel Government Data Portal](https://data.gov.il/dataset/tripscelular_1819).
- Additional data sources are specified in the respective folder READMEs where necessary.