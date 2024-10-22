import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import os

# Title of the web app
st.title("TRACK: Train Railway Analytics for Commuter Knowledge")

# Add a sidebar
st.sidebar.title("TRACK Dashboard")
st.sidebar.write("Use the options below to filter and explore station data.")


# Load the dataset with error handling
@st.cache_data
def load_data():
    if not os.path.exists("./datasets/gares-de-voyageurs.csv"):
        st.error("Data file not found.")
        return pd.DataFrame()  # Return an empty DataFrame
    return pd.read_csv("./datasets/gares-de-voyageurs.csv", delimiter=';')


stations_data = load_data()

if not stations_data.empty:
    # Split 'position_geographique' column into 'latitude' and 'longitude'
    stations_data[['latitude', 'longitude']] = stations_data['position_geographique'].str.split(',', expand=True)

    # Convert 'latitude' and 'longitude' columns to float
    stations_data['latitude'] = pd.to_numeric(stations_data['latitude'], errors='coerce')
    stations_data['longitude'] = pd.to_numeric(stations_data['longitude'], errors='coerce')

    # Drop rows with NaN values in 'latitude' or 'longitude'
    stations_data = stations_data.dropna(subset=['latitude', 'longitude'])

    # Define department to region mapping (only metropolitan regions)
    department_to_region = {
        '01': 'Auvergne-Rhône-Alpes', '02': 'Hauts-de-France', '03': 'Auvergne-Rhône-Alpes',
        '04': 'Provence-Alpes-Côte d\'Azur', '05': 'Provence-Alpes-Côte d\'Azur',
        '06': 'Provence-Alpes-Côte d\'Azur', '07': 'Auvergne-Rhône-Alpes', '08': 'Grand Est',
        '09': 'Occitanie', '10': 'Grand Est', '11': 'Occitanie', '12': 'Occitanie',
        '13': 'Provence-Alpes-Côte d\'Azur', '14': 'Normandie', '15': 'Auvergne-Rhône-Alpes',
        '16': 'Nouvelle-Aquitaine', '17': 'Nouvelle-Aquitaine', '18': 'Centre-Val de Loire',
        '19': 'Nouvelle-Aquitaine', '20': 'Île-de-France', '21': 'Bourgogne-Franche-Comté',
        '22': 'Bretagne', '23': 'Nouvelle-Aquitaine', '24': 'Nouvelle-Aquitaine',
        '25': 'Bourgogne-Franche-Comté', '26': 'Auvergne-Rhône-Alpes', '27': 'Normandie',
        '28': 'Centre-Val de Loire', '29': 'Bretagne', '30': 'Occitanie', '31': 'Occitanie',
        '32': 'Occitanie', '33': 'Nouvelle-Aquitaine', '34': 'Occitanie', '35': 'Bretagne',
        '36': 'Centre-Val de Loire', '37': 'Centre-Val de Loire', '38': 'Auvergne-Rhône-Alpes',
        '39': 'Bourgogne-Franche-Comté', '40': 'Nouvelle-Aquitaine', '41': 'Centre-Val de Loire',
        '42': 'Auvergne-Rhône-Alpes', '43': 'Auvergne-Rhône-Alpes', '44': 'Pays de la Loire',
        '45': 'Centre-Val de Loire', '46': 'Occitanie', '47': 'Nouvelle-Aquitaine',
        '48': 'Occitanie', '49': 'Pays de la Loire', '50': 'Normandie', '51': 'Grand Est',
        '52': 'Grand Est', '53': 'Pays de la Loire', '54': 'Grand Est', '55': 'Grand Est',
        '56': 'Bretagne', '57': 'Grand Est', '58': 'Bourgogne-Franche-Comté', '59': 'Hauts-de-France',
        '60': 'Hauts-de-France', '61': 'Normandie', '62': 'Hauts-de-France', '63': 'Auvergne-Rhône-Alpes',
        '64': 'Nouvelle-Aquitaine', '65': 'Occitanie', '66': 'Occitanie', '67': 'Grand Est',
        '68': 'Grand Est', '69': 'Auvergne-Rhône-Alpes', '70': 'Bourgogne-Franche-Comté',
        '71': 'Bourgogne-Franche-Comté', '72': 'Pays de la Loire', '73': 'Auvergne-Rhône-Alpes',
        '74': 'Auvergne-Rhône-Alpes', '75': 'Île-de-France', '76': 'Normandie',
        '77': 'Île-de-France', '78': 'Île-de-France', '79': 'Nouvelle-Aquitaine',
        '80': 'Hauts-de-France', '81': 'Occitanie', '82': 'Occitanie', '83': 'Provence-Alpes-Côte d\'Azur',
        '84': 'Provence-Alpes-Côte d\'Azur', '85': 'Pays de la Loire', '86': 'Nouvelle-Aquitaine',
        '87': 'Nouvelle-Aquitaine', '88': 'Grand Est', '89': 'Bourgogne-Franche-Comté',
        '90': 'Bourgogne-Franche-Comté', '91': 'Île-de-France', '92': 'Île-de-France',
        '93': 'Île-de-France', '94': 'Île-de-France', '95': 'Île-de-France'
    }

    # Define colors for each region
    region_colors = {
        'Auvergne-Rhône-Alpes': 'blue',
        'Bourgogne-Franche-Comté': 'green',
        'Bretagne': 'red',
        'Centre-Val de Loire': 'purple',
        'Grand Est': 'darkred',
        'Hauts-de-France': 'lightred',
        'Île-de-France': 'beige',
        'Normandie': 'darkblue',
        'Nouvelle-Aquitaine': 'darkgreen',
        'Occitanie': 'cadetblue',
        'Pays de la Loire': 'lightgreen',
        'Provence-Alpes-Côte d\'Azur': 'lightblue',
    }

    # Add filters in the sidebar
    unique_categories = stations_data['segment_drg'].str.split(';').explode().unique()
    unique_categories = [cat for cat in unique_categories if cat in ['A', 'B', 'C']]
    ordered_categories = ['All categories'] + sorted(unique_categories)

    category = st.sidebar.selectbox("Select a station category", ordered_categories)

    # Extract unique regions correctly
    stations_data['department'] = stations_data['codeinsee'].astype(str).str.zfill(5).str[:2]
    unique_regions = stations_data['department'].map(department_to_region).unique()

    region = st.sidebar.selectbox("Select a region (optional)", ['All regions'] + sorted(unique_regions.tolist()))

    # Dictionary for category meanings
    category_meanings = {
        'A': "National passenger stations: Frequented by at least 250,000 passengers per year.",
        'B': "Regional passenger stations: Frequented by at least 100,000 passengers per year.",
        'C': "Local passenger stations: Managed at the regional level.",
        'All categories': "Display all stations from all categories."
    }

    # Display the selected category meaning in the sidebar
    st.sidebar.write(f"**Meaning of category \"{category}\":**")
    st.sidebar.write(category_meanings[category])

    # Filter the data based on the selected category
    filtered_data = stations_data[
        stations_data['segment_drg'].str.contains(category)] if category != 'All categories' else stations_data

    # Further filter by region if specified
    if region != 'All regions':
        filtered_data = filtered_data[filtered_data['department'].map(department_to_region) == region]

    # Create a new column for regions based on department
    filtered_data['region'] = filtered_data['department'].map(department_to_region)

    # Count the number of stations in each region
    region_counts = filtered_data['region'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Number of Stations']

    # Plotting the number of stations per region using Plotly
    fig = px.bar(region_counts, x='Region', y='Number of Stations', color='Region',
                 title='Number of Stations by Region',
                 labels={'Number of Stations': 'Number of Stations', 'Region': 'Region'})

    st.plotly_chart(fig)  # Render the interactive plot

    st.subheader("Map of French Railway Stations")
    st.write(f"Showing {len(filtered_data)} stations in \"{category}\"")

    # Create a folium map based on the filtered data
    stations_map_filtered = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Add filtered markers to the map
    for idx, row in filtered_data.iterrows():
        codeinsee_str = str(row['codeinsee']).zfill(5)
        department_code = codeinsee_str[:2]
        region_name = department_to_region.get(department_code, 'Unknown Region')
        color = region_colors.get(region_name, 'black')

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['nom']}<br><b>Region:</b> {region_name}",
            icon=folium.Icon(color=color)
        ).add_to(stations_map_filtered)

    # Render the map
    folium_static(stations_map_filtered)

    # Improved legend section
    st.subheader("Légende des couleurs :")
    for region, color in region_colors.items():
        st.markdown(f"<span style='color:{color}; font-weight: bold;'>■ {region}</span>", unsafe_allow_html=True)

    st.write("Use the filters on the left to adjust the data displayed on the map and charts.")
else:
    st.write("No station data available to display.")
