#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 10:40:34 2024

@author: noamgal
"""


import pandas as pd
import geopandas as gpd
import pyproj
from datetime import datetime, timedelta

# Load data
zones_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/Shape_files/1270_02.09.2021.shp'
half_hour_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/AvgDayHalfHour6_20Trips201819_1270_weekday_v1.2.csv'
hourly_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/AvgDayHourlyTrips201819_1270_weekday_v1.csv'
hourly_arrival_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/AvgDayHourlyTrips201819_1270_weekday_arrival_v1.2.csv'

zones = gpd.read_file(zones_path)
half_hour_data = pd.read_csv(half_hour_path)
hourly_data = pd.read_csv(hourly_path)
hourly_arrival_data = pd.read_csv(hourly_arrival_path)

print('Datasets loaded')

# Calculate centroids
israel_tm_crs = pyproj.CRS.from_epsg(2039)  # Israel TM Grid
zones_tm = zones.to_crs(israel_tm_crs)
centroids_tm = zones_tm.geometry.centroid
centroids = centroids_tm.to_crs(epsg=4326)

# Create a dictionary of TAZ to centroid coordinates
taz_to_centroid = {taz: (lat, lon) for taz, (lat, lon) in zip(zones['TAZ_1270'], zip(centroids.y, centroids.x))}

def create_kepler_data(trip_data, focus_zone, direction='to', time_interval='hourly', min_trips=0.5, offset=0.0005):
    kepler_data = []
    
    from_col = 'fromZone' if direction == 'to' else 'ToZone'
    to_col = 'ToZone' if direction == 'to' else 'fromZone'
    
    focus_lat, focus_lon = taz_to_centroid[focus_zone]
    
    base_date = datetime(2019, 1, 1)  # Use January 1, 2019 as the base date
    
    for _, row in trip_data.iterrows():
        from_zone = row[from_col]
        to_zone = row[to_col]
        
        if direction == 'to' and to_zone != focus_zone:
            continue
        if direction == 'from' and from_zone != focus_zone:
            continue
        
        from_lat, from_lon = taz_to_centroid[from_zone]
        to_lat, to_lon = taz_to_centroid[to_zone]
        
        # Apply offset to both focus and non-focus zones
        if direction == 'to':
            from_lat -= offset
            to_lat += offset
        else:
            from_lat += offset
            to_lat -= offset
        
        if time_interval == 'hourly':
            time_columns = [f'h{hour}' for hour in range(24)]
        else:  # half-hourly
            time_columns = [f'h{hour}{minute:02d}' for hour in range(6, 20) for minute in [0, 30]]
        
        for time_col in time_columns:
            trips = row[time_col]
            if trips >= min_trips:
                if time_interval == 'hourly':
                    hour = int(time_col[1:])
                    time = base_date + timedelta(hours=hour)
                else:
                    hour = int(time_col[1:3])
                    minute = int(time_col[3:])
                    time = base_date + timedelta(hours=hour, minutes=minute)
                
                kepler_data.append({
                    'fromLat': from_lat,
                    'fromLon': from_lon,
                    'toLat': to_lat,
                    'toLon': to_lon,
                    'time': time.isoformat(),
                    'trips': round(trips * 2),  # Scale up the trips value
                    'hour': time.strftime('%H:%M'),  # Add readable time for tooltip
                    'direction': direction  # Add direction for filtering in Kepler.gl
                })
    
    return pd.DataFrame(kepler_data)

# Get focus zone from user
focus_zone = int(input("Please enter the focus zone ID: "))

# Process half-hourly data
print("Processing half-hourly data...")
to_focus_half_hourly = create_kepler_data(half_hour_data, focus_zone, direction='to', time_interval='half-hourly')
from_focus_half_hourly = create_kepler_data(half_hour_data, focus_zone, direction='from', time_interval='half-hourly')

# Process hourly data
print("Processing hourly data...")
to_focus_hourly = create_kepler_data(hourly_data, focus_zone, direction='to', time_interval='hourly')
from_focus_hourly = create_kepler_data(hourly_arrival_data, focus_zone, direction='from', time_interval='hourly')

# Save the data to CSV files
to_focus_half_hourly.to_csv(f'focus_{focus_zone}_to_half_hourly.csv', index=False)
from_focus_half_hourly.to_csv(f'focus_{focus_zone}_from_half_hourly.csv', index=False)
to_focus_hourly.to_csv(f'focus_{focus_zone}_to_hourly.csv', index=False)
from_focus_hourly.to_csv(f'focus_{focus_zone}_from_hourly.csv', index=False)

print(f"Data preprocessing complete. Files saved as:")
print(f"focus_{focus_zone}_to_half_hourly.csv")
print(f"focus_{focus_zone}_from_half_hourly.csv")
print(f"focus_{focus_zone}_to_hourly.csv")
print(f"focus_{focus_zone}_from_hourly.csv")

# Print sample output for verification
print("\nSample output (first 5 rows of hourly data to focus zone):")
print(to_focus_hourly.head().to_string())
print("\nData summary:")
print(to_focus_hourly.describe())
print("\nUnique time values:")
print(to_focus_hourly['hour'].unique())
print(f"\nTotal number of trips (hourly, to focus zone): {to_focus_hourly['trips'].sum()}")
print(f"\nTotal number of arcs (hourly, to focus zone): {len(to_focus_hourly)}")