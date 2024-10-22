import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Title and introduction
st.title("TRACK: Train Railway Analytics for Commuter Knowledge")
st.header("Explore and Compare Train Prices for 2024")

# Load the dataset with error handling
@st.cache_data
def load_prices_data():
    if not os.path.exists("./datasets/tarifs-tgv-inoui-ouigo.csv"):
        st.error("Data file not found.")
        return pd.DataFrame()  # Return an empty DataFrame
    return pd.read_csv("./datasets/tarifs-tgv-inoui-ouigo.csv", delimiter=';')

# Load data
prices_data = load_prices_data()

# Check if the dataset is loaded successfully
if prices_data.empty:
    st.stop()

# Convert necessary columns to numeric for calculations
prices_data['Prix minimum'] = pd.to_numeric(prices_data['Prix minimum'], errors='coerce')
prices_data['Prix maximum'] = pd.to_numeric(prices_data['Prix maximum'], errors='coerce')

# Sidebar for user input
st.sidebar.header("Select Your Route")

# Unique stations for dropdown
departure_stations = prices_data['Gare origine'].unique()
arrival_stations = prices_data['Destination'].unique()

selected_departure = st.sidebar.selectbox("Select Departure Station", options=departure_stations)
selected_destination = st.sidebar.selectbox("Select Arrival Station", options=arrival_stations)

# Filter data based on user input
filtered_data = prices_data[
    (prices_data['Gare origine'] == selected_departure) &
    (prices_data['Destination'] == selected_destination)
    ]

if not filtered_data.empty:
    # Show filtered prices
    st.subheader(f"Price Information from {selected_departure} to {selected_destination}")

    # Display Price Table
    price_summary = filtered_data[['Transporteur', 'Profil tarifaire', 'Prix minimum', 'Prix maximum']]
    price_summary = price_summary.reset_index(drop=True)
    price_summary.index = price_summary.index + 1
    st.dataframe(price_summary)

    # Box Plot
    fig_price_comparison = px.box(
        filtered_data,
        x='Transporteur',
        y=['Prix minimum', 'Prix maximum'],
        title=f'Price Distribution from {selected_departure} to {selected_destination}',
        labels={'value': 'Price (€)', 'variable': 'Price Type'}
    )

    st.plotly_chart(fig_price_comparison)


else:
    st.warning(f"No data available for the route from {selected_departure} to {selected_destination}.")


# Create a dictionary of estimated distances for common station pairs
distances = {
    ('AEROPORT CDG2 TGV ROISSY', 'MARSEILLE ST CHARLES'): 775,
    ('AEROPORT CDG2 TGV ROISSY', 'MONTPELLIER SUD DE FRANCE'): 750,
    ('AIX EN PROVENCE TGV', 'LYON-SAINT EXUPERY TGV'): 315,
    ('MARNE LA VALLEE CHESSY', 'AIX EN PROVENCE TGV'): 690,
    ('MARNE LA VALLEE CHESSY', 'POITIERS'): 350,
    ('PARIS MONTPARNASSE 1 ET 2', 'BORDEAUX ST JEAN'): 580,
    ('LYON PART DIEU', 'MARSEILLE ST CHARLES'): 315,
    ('LYON PART DIEU', 'PARIS GARE DE LYON'): 450,
    ('PARIS GARE DE LYON', 'NICE VILLE'): 935,
    ('PARIS GARE DE LYON', 'MARSEILLE ST CHARLES'): 775,
    ('PARIS GARE DE LYON', 'MONTPELLIER SUD DE FRANCE'): 745,
    ('PARIS GARE DE LYON', 'LYON PART DIEU'): 465,
    ('LYON PART DIEU', 'NICE VILLE'): 470,
    ('BORDEAUX ST JEAN', 'TOULOUSE MATABIAU'): 240,
    ('MARSEILLE ST CHARLES', 'TOULON'): 64,
    ('MARSEILLE ST CHARLES', 'AIX EN PROVENCE TGV'): 30,
    ('TOULOUSE MATABIAU', 'MONTPELLIER ST ROCH'): 245,
    ('PARIS GARE DE L\'EST', 'STRASBOURG'): 490,
    ('PARIS GARE DE L\'EST', 'REIMS'): 145,
    ('PARIS MONTPARNASSE 1 ET 2', 'RENNES'): 350,
    ('PARIS MONTPARNASSE 1 ET 2', 'NANTES'): 385,
    ('PARIS GARE DU NORD', 'LILLE EUROPE'): 225,
    ('LILLE EUROPE', 'LONDON ST PANCRAS'): 320,
    ('PARIS GARE DE LYON', 'GENEVA'): 410,
    ('PARIS GARE DE LYON', 'MILAN'): 850,
    ('NICE VILLE', 'MILAN'): 320,
    ('PARIS GARE DE LYON', 'ZURICH'): 655,
    ('LYON PART DIEU', 'GENEVA'): 150,
    ('LYON PART DIEU', 'BARCELONA SANTS'): 650,
    ('MARSEILLE ST CHARLES', 'BARCELONA SANTS'): 510,
    ('PARIS GARE DU NORD', 'BRUSSELS MIDI'): 315,
    ('PARIS GARE DU NORD', 'AMSTERDAM'): 520,
    ('MARNE LA VALLEE CHESSY', 'STRASBOURG'): 430,
    ('STRASBOURG', 'ZURICH'): 225,
    ('PARIS MONTPARNASSE 1 ET 2', 'LA ROCHELLE'): 480,
    ('PARIS MONTPARNASSE 1 ET 2', 'ANGERS ST LAUD'): 295,
    ('BORDEAUX ST JEAN', 'BAYONNE'): 185,
    ('BORDEAUX ST JEAN', 'PAU'): 225,
    ('TOULOUSE MATABIAU', 'PAU'): 210,
    ('NIMES', 'MONTPELLIER ST ROCH'): 55,
    ('LYON PART DIEU', 'DIJON VILLE'): 195,
    ('DIJON VILLE', 'PARIS GARE DE LYON'): 315,
    ('DIJON VILLE', 'STRASBOURG'): 330,
    ('LILLE EUROPE', 'BRUSSELS MIDI'): 110,
    ('NICE VILLE', 'MARSEILLE ST CHARLES'): 200,
    ('NICE VILLE', 'TOULON'): 150,
    ('NIMES', 'AVIGNON TGV'): 45,
    ('AVIGNON TGV', 'MARSEILLE ST CHARLES'): 85,
    ('LYON PART DIEU', 'GRENOBLE'): 105,
    ('PARIS GARE DE LYON', 'GRENOBLE'): 600,
    ('PARIS MONTPARNASSE 1 ET 2', 'LE MANS'): 210,
    ('PARIS MONTPARNASSE 1 ET 2', 'BREST'): 590,
    ('PARIS GARE DE L\'EST', 'LUXEMBOURG'): 375,
    ('PARIS GARE DE LYON', 'TOULOUSE MATABIAU'): 675,
    ('LILLE EUROPE', 'LYON PART DIEU'): 670,
    ('PARIS GARE DE LYON', 'VALENCE TGV'): 465
}

# Add a distance column based on the origin and destination pair
prices_data['Distance (km)'] = prices_data.apply(
    lambda row: distances.get((row['Gare origine'], row['Destination']),
                              distances.get((row['Destination'], row['Gare origine']), None)), axis=1)

# Drop rows where distance is not available
prices_data = prices_data.dropna(subset=['Distance (km)'])

# Calculate cost per km for both min and max prices
prices_data['Cost per km (Min)'] = prices_data['Prix minimum'] / prices_data['Distance (km)']
prices_data['Cost per km (Max)'] = prices_data['Prix maximum'] / prices_data['Distance (km)']

# Section 1: Table of Most Expensive Routes
st.subheader("Most Expensive Routes")

# Sort data by maximum price and display the top routes
most_expensive_routes = prices_data.sort_values(by='Prix maximum', ascending=False).head(10)
most_expensive_routes = most_expensive_routes.reset_index(drop=True)
most_expensive_routes.index = most_expensive_routes.index + 1
st.dataframe(most_expensive_routes[['Gare origine', 'Destination', 'Transporteur', 'Prix minimum', 'Prix maximum', 'Profil tarifaire', 'Distance (km)']])

# Section 2: Route Comparator (Cost per km)
st.subheader("Compare Routes by Cost per Kilometer")

# User selects two routes for comparison
st.write("Select two routes to compare their price per kilometer:")

route_1_origin = st.selectbox('Select Origin Station for Route 1', prices_data['Gare origine'].unique())
route_1_destination = st.selectbox('Select Destination Station for Route 1', prices_data['Destination'].unique())

route_2_origin = st.selectbox('Select Origin Station for Route 2', prices_data['Gare origine'].unique())
route_2_destination = st.selectbox('Select Destination Station for Route 2', prices_data['Destination'].unique())

# Filter the dataset for the selected routes
route_1_data = prices_data[
    (prices_data['Gare origine'] == route_1_origin) & (prices_data['Destination'] == route_1_destination)
]
route_2_data = prices_data[
    (prices_data['Gare origine'] == route_2_origin) & (prices_data['Destination'] == route_2_destination)
]

# Display comparison for Route 1
if not route_1_data.empty:
    st.write(f"### Route 1: {route_1_origin} to {route_1_destination}")
    st.write(f"Distance: {route_1_data['Distance (km)'].values[0]} km")
    st.write(f"Min Cost per km: {route_1_data['Cost per km (Min)'].values[0]:.2f} €/km")
    st.write(f"Max Cost per km: {route_1_data['Cost per km (Max)'].values[0]:.2f} €/km")
else:
    st.write(f"No data available for Route 1: {route_1_origin} to {route_1_destination}")

# Display comparison for Route 2
if not route_2_data.empty:
    st.write(f"### Route 2: {route_2_origin} to {route_2_destination}")
    st.write(f"Distance: {route_2_data['Distance (km)'].values[0]} km")
    st.write(f"Min Cost per km: {route_2_data['Cost per km (Min)'].values[0]:.2f} €/km")
    st.write(f"Max Cost per km: {route_2_data['Cost per km (Max)'].values[0]:.2f} €/km")
else:
    st.write(f"No data available for Route 2: {route_2_origin} to {route_2_destination}")