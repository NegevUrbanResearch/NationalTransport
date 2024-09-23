#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:30:00 2024
@author: noamgal
"""
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from datetime import datetime, timedelta

# Load data
zones_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/Shape_files/1270_02.09.2021.shp'
large_zones_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/Shape_files/33_02.09.2021.shp'
half_hour_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/AvgDayHalfHour6_20Trips201819_1270_weekday_v1.2.csv'

zones = gpd.read_file(zones_path)
large_zones = gpd.read_file(large_zones_path)
trip_data = pd.read_csv(half_hour_path)

# Calculate centroids
zones = zones.to_crs(epsg=3857)  # Use a projected CRS
large_zones = large_zones.to_crs(epsg=3857)
centroids = zones.geometry.centroid.to_crs(epsg=4326)
large_centroids = large_zones.geometry.centroid.to_crs(epsg=4326)

# Create dictionaries of TAZ to centroid coordinates
taz_to_centroid = {taz: (lat, lon) for taz, (lat, lon) in zip(zones['TAZ_1270'], zip(centroids.y, centroids.x))}
large_taz_to_centroid = {taz: (lat, lon) for taz, (lat, lon) in zip(large_zones['TAZ_33'], zip(large_centroids.y, large_centroids.x))}

# Create a mapping from TAZ_1270 to TAZ_33
taz_1270_to_33 = dict(zip(zones['TAZ_1270'], zones['TAZ_33']))

def determine_nearby_zones(focus_zone, zones, large_zones):
    focus_point = Point(taz_to_centroid[focus_zone])
    focus_large_zone = zones[zones['TAZ_1270'] == focus_zone]['TAZ_33'].iloc[0]
    
    # Get neighboring large zones
    neighboring_large_zones = large_zones[large_zones.touches(large_zones[large_zones['TAZ_33'] == focus_large_zone].geometry.iloc[0])]['TAZ_33'].tolist()
    neighboring_large_zones.append(focus_large_zone)
    
    # Get all small zones within these large zones
    nearby_zones = zones[zones['TAZ_33'].isin(neighboring_large_zones)]['TAZ_1270'].tolist()
    
    return set(nearby_zones)

def create_kepler_data(trip_data, focus_zone, direction='to', min_trips=0.5):
    nearby_zones = determine_nearby_zones(focus_zone, zones, large_zones)
    kepler_data = []
    
    from_col = 'fromZone' if direction == 'to' else 'ToZone'
    to_col = 'ToZone' if direction == 'to' else 'fromZone'
    
    focus_lat, focus_lon = taz_to_centroid[focus_zone]
    base_date = datetime(2018, 1, 1)  # Use a fixed date for consistency
    
    for _, row in trip_data.iterrows():
        from_zone = row[from_col]
        to_zone = row[to_col]
        
        if direction == 'to' and to_zone != focus_zone:
            continue
        if direction == 'from' and from_zone != focus_zone:
            continue
        
        if from_zone in nearby_zones:
            from_lat, from_lon = taz_to_centroid[from_zone]
        else:
            large_zone = taz_1270_to_33[from_zone]
            from_lat, from_lon = large_taz_to_centroid[large_zone]
        
        if to_zone in nearby_zones:
            to_lat, to_lon = taz_to_centroid[to_zone]
        else:
            large_zone = taz_1270_to_33[to_zone]
            to_lat, to_lon = large_taz_to_centroid[large_zone]
        
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
                        'trips': round(trips),  # Scale up the trips value
                        'hour': f"{hour:02d}:{minute:02d}"  # Add readable time for tooltip
                    })
    
    return pd.DataFrame(kepler_data)

# Get focus zone from user
focus_zone = int(input("Please enter the focus zone ID: "))

# Create and save Kepler.gl formatted data
to_focus_data = create_kepler_data(trip_data, focus_zone, direction='to', min_trips=0.5)
from_focus_data = create_kepler_data(trip_data, focus_zone, direction='from', min_trips=0.5)

# Combine to and from data
combined_data = pd.concat([to_focus_data, from_focus_data], ignore_index=True)
combined_data.to_csv(f'focus_{focus_zone}_kepler_animated_mixed.csv', index=False)

print(f"Data preprocessing complete. File saved as 'focus_{focus_zone}_kepler_animated_mixed.csv'")

# Print sample output for verification
print("\nSample output (first 5 rows of combined data):")
print(combined_data.head().to_string())

print("\nData summary:")
print(combined_data.describe())

print("\nUnique time values:")
print(combined_data['hour'].unique())

print(f"\nTotal number of trips: {len(combined_data)}")

# Additional statistics
print("\nNumber of unique origin points:")
print(combined_data[['fromLat', 'fromLon']].drop_duplicates().shape[0])

print("\nNumber of unique destination points:")
print(combined_data[['toLat', 'toLon']].drop_duplicates().shape[0])

print("\nTotal trips by hour:")
print(combined_data.groupby('hour')['trips'].sum().sort_index())