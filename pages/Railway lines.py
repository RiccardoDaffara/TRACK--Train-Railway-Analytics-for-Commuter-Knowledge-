import os
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import json
import plotly.express as px

# Title of the web app
st.title("TRACK: Train Railway Analytics for Commuter Knowledge")

# Add a brief introduction to the app
st.markdown("""
    This application provides insights into the railway lines in France. 
    You can explore the different types of train lines, including conventional and high-speed lines. 
    Hover over the lines on the map to view additional details such as the line name, category, and length.
""")

# Load the GeoJSON file from the repository
@st.cache_data
def load_geojson(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Path to your GeoJSON file
geojson_file_path = './datasets/lignes-lgv-et-par-ecartement.geojson'

# Load the GeoJSON data
geojson_data = load_geojson(geojson_file_path)

# Function to get the value before '+' or '-'
def extract_value(value_str):
    try:
        return int(value_str.split('+')[0].split('-')[0])
    except (ValueError, IndexError):
        return None

# Add lengths to the features
for feature in geojson_data['features']:
    pkd_str = feature['properties'].get('pkd', '0')
    pkf_str = feature['properties'].get('pkf', '0')

    pkd = extract_value(pkd_str)
    pkf = extract_value(pkf_str)

    if pkd is not None and pkf is not None:
        line_length = pkf - pkd
        feature['properties']['longueur'] = line_length
    else:
        feature['properties']['longueur'] = None

# Create a Folium map centered around France
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Define a color mapping for 'catlig' values
color_mapping = {
    'Ligne du réseau conventionnel': 'green',
    'Ligne à grande vitesse': 'blue'
}

# Create separate GeoJSON layers for each category
conventional_lines = folium.FeatureGroup(name='Ligne du réseau conventionnel', show=True)
high_speed_lines = folium.FeatureGroup(name='Ligne à grande vitesse', show=True)

# Define a style function based on 'catlig'
def style_function(feature):
    category = feature['properties']['catlig']
    color = color_mapping.get(category, 'black')
    return {
        'fillColor': color,
        'color': color,
        'weight': 2,
        'fillOpacity': 0.6,
    }

# Create a list of fields to display in the tooltip
tooltip_fields = ['lib_ligne', 'catlig', 'longueur']

# Create a tooltip with aliases
tooltip_aliases = {
    'lib_ligne': 'Line Name:',
    'catlig': 'Category:',
    'longueur': 'Length (km):'
}

# Add features to the respective layers based on their category
for feature in geojson_data['features']:
    category = feature['properties']['catlig']
    if category in color_mapping:
        layer = conventional_lines if category == 'Ligne du réseau conventionnel' else high_speed_lines
        layer.add_child(folium.GeoJson(
            feature,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=[tooltip_aliases[field] for field in tooltip_fields],
                localize=True,
                sticky=True,
                labels=True,
            )
        ))

# Add layers to the map
conventional_lines.add_to(m)
high_speed_lines.add_to(m)

# Add layer control to the map
folium.LayerControl().add_to(m)

# Display the map in Streamlit
folium_static(m)

# Optional: Display total length of all lines
total_length = sum(feature['properties']['longueur'] for feature in geojson_data['features'] if feature['properties']['longueur'] is not None)
st.write(f"Total Length of all Train Lines: {total_length} km")

# Create a bar chart for the number of lines by category
line_counts = pd.Series(
    {category: sum(1 for feature in geojson_data['features'] if feature['properties']['catlig'] == category)
     for category in color_mapping.keys()}
).reset_index()
line_counts.columns = ['Category', 'Count']

# Create a Plotly bar chart with the corresponding colors
fig = px.bar(line_counts,
             x='Category',
             y='Count',
             color='Category',
             color_discrete_map=color_mapping,  # Use the same color mapping for the plot
             title='Number of Train Lines by Category',
             labels={'Count': 'Number of Lines', 'Category': 'Train Line Categories'})

# Display the Plotly chart
st.plotly_chart(fig)

# Add a note about data source
st.markdown("""
    **Data Source:** This data is sourced from the SNCF and contains information about various train lines in France.
""")
