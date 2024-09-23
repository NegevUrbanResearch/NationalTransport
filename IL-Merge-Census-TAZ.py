#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 17:10:19 2024

@author: noamgal
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from typing import List, Dict, Any
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define file paths
TAZ_SHAPEFILE = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/Shape_files/1270_02.09.2021.shp'
POPULATION_EXCEL = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/Clean_TAZ1270_population.xlsx'
CENSUS_EXCEL = '/Users/noamgal/Downloads/NUR/IL-Census-2022/census_2022.xlsx'
OUTPUT_CSV = '/Users/noamgal/Downloads/NUR/taz_census_estimate.csv'

# Define economic statistics to include
ECONOMIC_STATS = [
    'pop_density', 'sexRatio', 'inst_pcnt', 'Foreign_pcnt',
    'age0_19_pcnt', 'age20_64_pcnt', 'age65_pcnt', 'DependencyRatio',
    'age_median', 'm_age_median', 'w_age_median', 'married18_34_pcnt',
    'married45_54_pcnt', 'j_isr_pcnt', 'j_abr_pcnt', 'aliya2002_pcnt',
    'aliya2010_pcnt', 'israel_pcnt', 'asia_pcnt', 'africa_pcnt',
    'europe_pcnt', 'america_pcnt', 'MarriageAge_mdn', 'm_MarriageAge_mdn',
    'w_MarriageAge_mdn', 'ChldBorn_avg', 'koshi5_pcnt', 'koshi65_pcnt',
    'AcadmCert_pcnt', 'WrkY_pcnt', 'Empl_pcnt', 'SelfEmpl_pcnt',
    'HrsWrkWk_avg', 'Wrk_15_17_pcnt', 'WrkOutLoc_pcnt',
    'employeesAnnual_medWage', 'EmployeesWage_decile9Up',
    'SelfEmployedAnnual_medWage', 'SelfEmployedWage_decile9Up',
    'size_avg', 'hh0_5_pcnt', 'hh18_24_pcnt', 'Computer_avg',
    'Vehicle0_pcnt', 'Vehicle2up_pcnt', 'Parking_pcnt', 'own_pcnt',
    'rent_pcnt'
]

def load_and_prepare_data() -> tuple:
    """
    Load and prepare the TAZ, population, and census data.
    """
    logging.info("Loading and preparing data...")
    
    # Load TAZ shapefile
    zones = gpd.read_file(TAZ_SHAPEFILE)
    
    # Load and prepare population data
    population_df = pd.read_excel(POPULATION_EXCEL)
    population_df = population_df.rename(columns={'TAZ_1270': 'TAZ', 'Local_Code': 'LocalityCode'})
    
    # Load and prepare census data
    census_df = pd.read_excel(CENSUS_EXCEL)
    census_df = census_df.rename(columns={'LocalityCode': 'LocalityCode', 'StatArea': 'StatisticalZone'})
    
    # Clean and convert StatisticalZone
    census_df['StatisticalZone'] = census_df['StatisticalZone'].apply(clean_stat_zone)
    
    # Ensure LocalityCodes are strings
    population_df['LocalityCode'] = population_df['LocalityCode'].astype(str)
    census_df['LocalityCode'] = census_df['LocalityCode'].astype(str)
    
    return zones, population_df, census_df

def clean_stat_zone(zone: Any) -> int:
    """
    Clean and convert statistical zone to integer.
    """
    if pd.isna(zone) or zone == '':
        return -1
    try:
        return int(str(zone).split('+')[0])
    except ValueError:
        return -1

def create_taz_mapping(population_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a mapping between TAZ and statistical zones/localities.
    """
    logging.info("Creating TAZ mapping...")
    taz_mapping = population_df[['TAZ', 'LocalityCode', 'Statistical_Zone']].drop_duplicates()
    taz_mapping['Statistical_Zone_List'] = taz_mapping['Statistical_Zone'].apply(split_stat_zones)
    return taz_mapping

def split_stat_zones(zone_str: str) -> List[int]:
    """
    Split and clean statistical zones.
    """
    if pd.isna(zone_str):
        return []
    return [int(z.strip()) for z in str(zone_str).split(',') if z.strip()]

def get_taz_stats(row: pd.Series, census_df: pd.DataFrame) -> pd.Series:
    """
    Get statistics for a TAZ.
    """
    stats = census_df[(census_df['StatisticalZone'].isin(row['Statistical_Zone_List'])) & 
                      (census_df['LocalityCode'] == row['LocalityCode'])]
    
    if not stats.empty:
        return stats[ECONOMIC_STATS].mean()
    else:
        locality_stats = census_df[(census_df['LocalityCode'] == row['LocalityCode']) & 
                                   (census_df['StatisticalZone'] == -1)]
        if not locality_stats.empty:
            return locality_stats[ECONOMIC_STATS].mean()
        else:
            return pd.Series({col: np.nan for col in ECONOMIC_STATS})

def calculate_taz_stats(taz_mapping: pd.DataFrame, census_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate statistics for each TAZ.
    """
    logging.info("Calculating TAZ statistics...")
    taz_stats = taz_mapping.apply(lambda row: get_taz_stats(row, census_df), axis=1)
    return pd.concat([taz_mapping[['TAZ', 'LocalityCode', 'Statistical_Zone']], taz_stats], axis=1)

def validate_results(final_df: pd.DataFrame, population_df: pd.DataFrame, census_df: pd.DataFrame) -> None:
    """
    Validate the results of the merge process.
    """
    logging.info("Validating results...")
    
    # Check for missing data
    missing_data = final_df[ECONOMIC_STATS].isnull().sum()
    logging.info(f"Columns with missing data:\n{missing_data[missing_data > 0]}")
    
    # Check for unexpected values
    for col in ECONOMIC_STATS:
        if col in final_df.columns:
            unexpected = final_df[(final_df[col] < 0) | (final_df[col] > 100)][['TAZ', 'LocalityCode', col]]
            if not unexpected.empty:
                logging.warning(f"Unexpected values in {col}:\n{unexpected}")
    
    # Compare total population
    taz_pop = final_df['pop_density'].sum()
    census_pop = census_df['pop_approx'].sum()
    logging.info(f"Total population - TAZ: {taz_pop:.0f}, Census: {census_pop:.0f}")
    if abs(taz_pop - census_pop) / census_pop > 0.1:
        logging.warning("Large discrepancy in total population")
    
    # Check coverage
    taz_coverage = len(final_df) / len(population_df)
    locality_coverage = final_df['LocalityCode'].nunique() / census_df['LocalityCode'].nunique()
    logging.info(f"TAZ coverage: {taz_coverage:.2%}")
    logging.info(f"Locality coverage: {locality_coverage:.2%}")

def main():
    # Load and prepare data
    zones, population_df, census_df = load_and_prepare_data()
    
    # Create TAZ mapping
    taz_mapping = create_taz_mapping(population_df)
    
    # Calculate TAZ statistics
    final_df = calculate_taz_stats(taz_mapping, census_df)
    
    # Round values
    for col in ECONOMIC_STATS:
        if col in final_df.columns:
            final_df[col] = final_df[col].round(2)
    
    # Validate results
    validate_results(final_df, population_df, census_df)
    
    # Save the final DataFrame
    final_df.to_csv(OUTPUT_CSV, index=False)
    logging.info(f"File saved successfully at: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()