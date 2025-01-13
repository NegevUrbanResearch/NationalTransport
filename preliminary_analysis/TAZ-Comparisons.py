import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from branca.colormap import LinearColormap

def set_dark_mode_style():
    """Set global dark mode style for matplotlib"""
    plt.style.use('dark_background')
    dark_bg_color = '#1a1a1a'
    text_color = '#ffffff'
    grid_color = '#333333'
    
    plt.rcParams.update({
        'figure.facecolor': dark_bg_color,
        'axes.facecolor': dark_bg_color,
        'axes.edgecolor': text_color,
        'axes.labelcolor': text_color,
        'text.color': text_color,
        'xtick.color': text_color,
        'ytick.color': text_color,
        'grid.color': grid_color,
        'savefig.facecolor': dark_bg_color
    })

def load_data():
    """Load all required datasets"""
    base_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3'
    zones = gpd.read_file(f'{base_path}/Shape_files/1270_02.09.2021.shp').to_crs(epsg=3857)
    population_df = pd.read_excel(f'{base_path}/1270_population.xlsx')
    df_weekday = pd.read_csv(f'{base_path}/AvgDayHourlyTrips201819_1270_weekday_v1.csv')
    df_weekday_arrival = pd.read_csv(f'{base_path}/AvgDayHourlyTrips201819_1270_weekday_arrival_v1.2.csv')
    
    return zones, population_df, df_weekday, df_weekday_arrival

def plot_time_profile(df_weekday, df_weekday_arrival, zone_id, title):
    """Create a dark mode time profile plot for a zone"""
    set_dark_mode_style()
    
    # Prepare data
    to_zone = df_weekday_arrival[df_weekday_arrival['ToZone'] == zone_id]
    from_zone = df_weekday[df_weekday['fromZone'] == zone_id]
    
    time_cols = [f'h{i}' for i in range(24)]
    arrivals = (to_zone[time_cols].sum() / to_zone[time_cols].sum().sum()) * 100
    departures = (from_zone[time_cols].sum() / from_zone[time_cols].sum().sum()) * 100
    
    # Create plot
    fig, ax = plt.subplots(figsize=(15, 8))
    hours = range(24)
    x = np.arange(24)
    width = 0.35
    
    # Plot with enhanced styling
    rects1 = ax.bar(x + 0.5 - width/2, arrivals, width, label='Arrivals', 
                    color='#3498db', alpha=0.7)
    rects2 = ax.bar(x + 0.5 + width/2, departures, width, label='Departures', 
                    color='#e74c3c', alpha=0.7)
    
    # Styling
    plt.title(title, fontsize=32, pad=20)
    plt.xlabel('Hour of Day', fontsize=18, labelpad=15)
    plt.ylabel('Percentage of Daily Trips', fontsize=18, labelpad=15)
    plt.tight_layout()
    ax.set_xticks(range(24))
    ax.set_xticklabels(hours)
    ax.legend(fontsize=16)
    ax.grid(True, axis='x', linestyle='--', alpha=0.2)
    ax.set_xlim(-0.5, 23.5)
    
    # Add direct annotations on bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, fontsize=8,
                        color='white')
    
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    output_path = f'/Users/noamgal/Downloads/NUR/celular1819_v1.3/time_signature_zone_{zone_id}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='#1a1a1a', edgecolor='none')
    print(f"Time profile plot saved to {output_path}")
    plt.close()

def compare_zones(df_weekday, df_weekday_arrival, zone1_id, zone2_id, 
                 zone1_name, zone2_name):
    """Compare time profiles of two zones in dark mode"""
    set_dark_mode_style()
    
    def prepare_zone_data(zone):
        to_zone = df_weekday_arrival[df_weekday_arrival['ToZone'] == zone]
        from_zone = df_weekday[df_weekday['fromZone'] == zone]
        
        time_columns = [f'h{i}' for i in range(24)]
        arrivals = (to_zone[time_columns].sum() / to_zone[time_columns].sum().sum()) * 100
        departures = (from_zone[time_columns].sum() / from_zone[time_columns].sum().sum()) * 100
        
        # Reset index to numeric values
        arrivals.index = range(24)
        departures.index = range(24)
        
        return arrivals, departures

    arrivals1, departures1 = prepare_zone_data(zone1_id)
    arrivals2, departures2 = prepare_zone_data(zone2_id)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(16, 10))
    hours = range(24)

    # Plot lines with markers
    plt.plot(hours, arrivals1, color='#3498db', linestyle='-', linewidth=2, 
             marker='o', markersize=6, label=f'{zone1_name} Arrivals')
    plt.plot(hours, departures1, color='#2980b9', linestyle='--', linewidth=2, 
             marker='s', markersize=6, label=f'{zone1_name} Departures')
    plt.plot(hours, arrivals2, color='#e74c3c', linestyle='-', linewidth=2, 
             marker='o', markersize=6, label=f'{zone2_name} Arrivals')
    plt.plot(hours, departures2, color='#c0392b', linestyle='--', linewidth=2, 
             marker='s', markersize=6, label=f'{zone2_name} Departures')

    # Customize the plot
    plt.title('Beer Sheva Innovation District vs Matam Haifa', 
             fontsize=36, fontweight='bold', pad=20)
    plt.xlabel('Hour of Day', fontsize=18)
    plt.ylabel('Percentage of Daily Trips', fontsize=18)
    plt.xticks(hours, fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.2)

    # Add legend
    plt.legend(fontsize=18, loc='upper left')

    # Function to annotate peaks
    def annotate_peak(data, color, label):
        peak_hour = data.idxmax()
        peak_value = data.max()
        plt.annotate(f'{peak_value:.1f}%',
                     xy=(peak_hour, peak_value),
                     xytext=(0, 5),
                     textcoords='offset points',
                     ha='center',
                     va='bottom',
                     color=color,
                     fontsize=10,
                     fontweight='bold')

    # Add peak annotations
    annotate_peak(arrivals1, '#3498db', f'{zone1_name} Arrivals')
    annotate_peak(departures1, '#2980b9', f'{zone1_name} Departures')
    annotate_peak(arrivals2, '#e74c3c', f'{zone2_name} Arrivals')
    annotate_peak(departures2, '#c0392b', f'{zone2_name} Departures')

    
    plt.tight_layout()
    output_path = f'/Users/noamgal/Downloads/NUR/celular1819_v1.3/comparison_{zone1_id}_vs_{zone2_id}_dark.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='#1a1a1a', edgecolor='none')
    print(f"Comparison plot saved to {output_path}")
    plt.close()

def main():
    # Load data
    zones, population_df, df_weekday, df_weekday_arrival = load_data()
    
    # Innovation District analysis
    innovation_district = 101104
    plot_time_profile(
        df_weekday, df_weekday_arrival,
        innovation_district,
        'Beer Sheva Innovation District Daily Pattern'
    )
    
    # Matam analysis
    matam = 100694
    plot_time_profile(
        df_weekday, df_weekday_arrival,
        matam,
        'Matam Haifa Daily Pattern'
    )
    
    # Compare zones
    compare_zones(
        df_weekday, df_weekday_arrival,
        innovation_district, matam,
        'Beer Sheva ID', 'Matam Haifa'
    )

if __name__ == "__main__":
    main()

def prepare_data_for_export(df_weekday, df_weekday_arrival, zone_ids, zone_names):
    """Prepare time profile data for export"""
    formatted_data = []
    
    for zone_id, zone_name in zip(zone_ids, zone_names):
        # Get arrival and departure data
        to_zone = df_weekday_arrival[df_weekday_arrival['ToZone'] == zone_id]
        from_zone = df_weekday[df_weekday['fromZone'] == zone_id]
        
        time_cols = [f'h{i}' for i in range(24)]
        arrivals = (to_zone[time_cols].sum() / to_zone[time_cols].sum().sum()) * 100
        departures = (from_zone[time_cols].sum() / from_zone[time_cols].sum().sum()) * 100
        
        # Format data for each hour
        for hour in range(24):
            formatted_data.append({
                'zone_id': zone_id,
                'zone_name': zone_name,
                'hour': hour,
                'time': f'{hour:02d}:00',
                'arrivals': round(arrivals[f'h{hour}'], 2),
                'departures': round(departures[f'h{hour}'], 2),
                'total_trips': round(arrivals[f'h{hour}'] + departures[f'h{hour}'], 2)
            })
    
    return pd.DataFrame(formatted_data)

def export_data(df_weekday, df_weekday_arrival):
    """Export formatted data to CSV"""
    # Define zones and their names
    zones = {
        101104: 'Beer Sheva Innovation District',
        100694: 'Matam Haifa'
    }
    
    # Prepare and export data
    data = prepare_data_for_export(
        df_weekday, 
        df_weekday_arrival, 
        list(zones.keys()), 
        list(zones.values())
    )
    
    # Export to CSV
    output_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/zone_time_profiles.csv'
    data.to_csv(output_path, index=False)
    print(f"Data exported to {output_path}")
    
    # Print sample of the data
    print("\nSample of exported data:")
    print(data.head())
    
    # Print summary statistics
    print("\nSummary statistics:")
    for zone_name in zones.values():
        zone_data = data[data['zone_name'] == zone_name]
        print(f"\n{zone_name}:")
        print(f"Peak Arrivals: {zone_data['arrivals'].max():.2f}% at {zone_data.loc[zone_data['arrivals'].idxmax(), 'time']}")
        print(f"Peak Departures: {zone_data['departures'].max():.2f}% at {zone_data.loc[zone_data['departures'].idxmax(), 'time']}")

def main():
    # Load data
    zones, population_df, df_weekday, df_weekday_arrival = load_data()
    
    # Export formatted data
    export_data(df_weekday, df_weekday_arrival)

if __name__ == "__main__":
    main()