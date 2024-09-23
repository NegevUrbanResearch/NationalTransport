#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 22:14:55 2024

@author: noamgal
"""

import pandas as pd
import geopandas as gpd
import pyproj
from datetime import datetime, timedelta

# Load data
zones_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/Shape_files/1270_02.09.2021.shp'
half_hour_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/AvgDayHalfHour6_20Trips201819_1270_weekday_v1.2.csv'
zones = gpd.read_file(zones_path)
trip_data = pd.read_csv(half_hour_path)

# Calculate centroids
israel_tm_crs = pyproj.CRS.from_epsg(2039)  # Israel TM Grid
zones_tm = zones.to_crs(israel_tm_crs)
centroids_tm = zones_tm.geometry.centroid
centroids = centroids_tm.to_crs(epsg=4326)

# Create a dictionary of TAZ to centroid coordinates
taz_to_centroid = {taz: (lat, lon) for taz, (lat, lon) in zip(zones['TAZ_1270'], zip(centroids.y, centroids.x))}

# Function to create Kepler.gl formatted data with offset
def create_kepler_data(trip_data, focus_zone, direction='to', min_trips=0.5, offset=0.001):
    kepler_data = []
    
    from_col = 'fromZone' if direction == 'to' else 'ToZone'
    to_col = 'ToZone' if direction == 'to' else 'fromZone'
    
    focus_lat, focus_lon = taz_to_centroid[focus_zone]
    
    # Apply offset to focus zone
    if direction == 'to':
        focus_lat += offset
    else:
        focus_lat -= offset
    
    base_date = datetime(2018, 1, 1)  # Use a fixed date for consistency
    
    for _, row in trip_data.iterrows():
        from_zone = row[from_col]
        to_zone = row[to_col]
        
        if direction == 'to' and to_zone != focus_zone:
            continue
        if direction == 'from' and from_zone != focus_zone:
            continue
        
        from_lat, from_lon = taz_to_centroid[from_zone]
        to_lat, to_lon = taz_to_centroid[to_zone]
        
        # Apply offset to non-focus zone
        if direction == 'to':
            from_lat -= offset
        else:
            to_lat += offset
        
        for hour in range(6, 20):
            for minute in [0, 30]:
                time_key = f'h{hour}{minute:02d}'
                trips = row[time_key]
                if trips >= min_trips:
                    time = base_date + timedelta(hours=hour, minutes=minute)
                    kepler_data.append({
                        'fromLat': from_lat,
                        'fromLon': from_lon,
                        'toLat': focus_lat if direction == 'to' else to_lat,
                        'toLon': focus_lon if direction == 'to' else to_lon,
                        'time': time.isoformat(),
                        'trips': round(trips * 2),  # Scale up the trips value
                        'hour': f"{hour:02d}:{minute:02d}",  # Add readable time for tooltip
                        'direction': direction  # Add direction for filtering in Kepler.gl
                    })
    
    return pd.DataFrame(kepler_data)

# Get focus zone from user
focus_zone = int(input("Please enter the focus zone ID: "))

# Create and save Kepler.gl formatted data
to_focus_data = create_kepler_data(trip_data, focus_zone, direction='to', min_trips=0.5)
from_focus_data = create_kepler_data(trip_data, focus_zone, direction='from', min_trips=0.5)

# Combine to and from data
combined_data = pd.concat([to_focus_data, from_focus_data], ignore_index=True)
combined_data.to_csv(f'focus_{focus_zone}_kepler_arc_map.csv', index=False)
print(f"Data preprocessing complete. File saved as 'focus_{focus_zone}_kepler_arc_map.csv'")

# Print sample output for verification
print("\nSample output (first 5 rows of combined data):")
print(combined_data.head().to_string())
print("\nData summary:")
print(combined_data.describe())
print("\nUnique time values:")
print(combined_data['hour'].unique())
print(f"\nTotal number of trips: {combined_data['trips'].sum()}")
print(f"\nTotal number of arcs: {len(combined_data)}")