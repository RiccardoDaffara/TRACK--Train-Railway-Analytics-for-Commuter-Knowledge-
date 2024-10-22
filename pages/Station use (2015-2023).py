import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Title of the web app
st.title("TRACK: Train Railway Analytics for Commuter Knowledge")


# Load the dataset with error handling
@st.cache_data
def load_data():
    if not os.path.exists("./datasets/frequentation-gares.csv"):
        st.error("Data file not found.")
        return pd.DataFrame()  # Return an empty DataFrame
    return pd.read_csv("./datasets/frequentation-gares.csv", delimiter=';')


frequentation_data = load_data()

# Show the dataframe
if not frequentation_data.empty:
    # Drop rows with NaN values
    frequentation_data = frequentation_data.dropna()

    # Sidebar: Filter by category and year
    st.sidebar.title("TRACK Dashboard")

    # Add a filter for station categories
    unique_categories = frequentation_data['segmentation_drg'].str.split(';').explode().unique()
    unique_categories = [cat for cat in unique_categories if cat in ['A', 'B', 'C']]  # Filter for only A, B, C
    ordered_categories = ['All categories'] + sorted(unique_categories)

    with st.sidebar.expander("Station Filter"):
        st.sidebar.write("Select a category to filter the stations.")
        category = st.sidebar.selectbox("Station Category", ordered_categories)

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

    # Available years for the data
    available_years = ['2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015']

    with st.sidebar.expander("Year Selection"):
        st.sidebar.write("Select a year to see the top frequented stations.")
        selected_year = st.sidebar.selectbox("Select a Year", available_years, index=0)

    st.subheader(f"Top 10 of the most frequented stations for the year {selected_year}:")

    # Filter the data based on the selected category
    filtered_data = frequentation_data if category == 'All categories' else frequentation_data[
        frequentation_data['segmentation_drg'].str.contains(category)]

    # Filter and sort the 10 most frequented stations for the selected year
    top_10_stations = filtered_data[['nom_gare', 'total_voyageurs_' + selected_year]].nlargest(10,
                                                                                               'total_voyageurs_' + selected_year)

    # Add a rank column
    top_10_stations.insert(0, 'Rank', range(1, len(top_10_stations) + 1))

    # Display the interactive table
    st.sidebar.write("### Top 10 Most Frequented Stations")
    st.sidebar.dataframe(top_10_stations.set_index('Rank'))

    # Display an interactive bar chart of the most frequented stations
    fig = px.bar(top_10_stations, x='nom_gare', y='total_voyageurs_' + selected_year,
                 title=f"Top 10 stations for {selected_year}:",
                 labels={'nom_gare': 'Station Name', 'total_voyageurs_' + selected_year: 'Number of Passengers'},
                 color_discrete_sequence=['#1f77b4'])  # Custom color for bar
    st.sidebar.plotly_chart(fig)

    # Main Area: Comparison Analysis
    st.header("Comparison and Trends Analysis")

    # New Section: Compare passenger numbers for selected stations and years
    with st.expander("Comparison Analysis"):
        st.write("Compare passenger numbers across different years for selected stations.")

        # Choose between pre-COVID and post-COVID years
        comparison_years = st.multiselect("Select Years to Compare:", available_years, default=['2015', '2021'])

        # Select specific stations for comparison
        station_names = filtered_data['nom_gare'].unique()
        selected_stations = st.multiselect("Select Stations for Comparison:", station_names,
                                           default=top_10_stations['nom_gare'].tolist())  # Default stations

        if selected_stations and comparison_years:
            comparison_data = filtered_data[
                ['nom_gare'] + ['total_voyageurs_' + year for year in comparison_years]].copy()

            # Filter for selected stations
            comparison_data = comparison_data[comparison_data['nom_gare'].isin(selected_stations)]

            # Melt the DataFrame for easier plotting
            comparison_data = comparison_data.melt(id_vars=['nom_gare'], var_name='Year', value_name='Total Passengers')

            # Convert Year to a categorical type to control order
            comparison_data['Year'] = comparison_data['Year'].str.replace('total_voyageurs_', '')
            comparison_data['Year'] = pd.Categorical(comparison_data['Year'], categories=comparison_years, ordered=True)

            # Sort the data by Year
            comparison_data.sort_values('Year', inplace=True)

            # Display a horizontal bar chart comparing passenger numbers
            comparison_fig = px.bar(comparison_data, x='nom_gare', y='Total Passengers', color='Year',
                                    title="Comparison of Passenger Numbers Across Selected Years",
                                    labels={'nom_gare': 'Station Name', 'Total Passengers': 'Number of Passengers'},
                                    opacity=0.7,
                                    color_discrete_sequence=px.colors.qualitative.Plotly)  # Using Plotly color palette
            comparison_fig.update_layout(barmode='group')
            st.plotly_chart(comparison_fig)
        else:
            st.warning("Please select at least one station and one year for comparison.")

    # Yearly Passenger Trends Section
    with st.expander("Yearly Trends"):
        st.write("Analyze passenger trends for a selected station over the years.")
        selected_station_trend = st.selectbox("Select a Station for Trend Analysis:", station_names)
        trend_data = filtered_data[filtered_data['nom_gare'] == selected_station_trend]

        # Prepare the data for plotting
        trend_data = trend_data.melt(id_vars=['nom_gare'],
                                     value_vars=[f'total_voyageurs_{year}' for year in available_years],
                                     var_name='Year', value_name='Total Passengers')
        trend_data['Year'] = trend_data['Year'].str.replace('total_voyageurs_', '')

        # Plotting the line chart
        line_fig = px.line(trend_data, x='Year', y='Total Passengers',
                           title=f"Passenger Trends for {selected_station_trend} Station:",
                           labels={'Total Passengers': 'Number of Passengers', 'Year': 'Year'},
                           markers=True)  # Adding markers for better visibility
        st.plotly_chart(line_fig)

    # Footer note about data source
    st.markdown("""
        **Data Source:** This data is sourced from SNCF and contains information about passenger frequency at various train stations in France.
    """)
