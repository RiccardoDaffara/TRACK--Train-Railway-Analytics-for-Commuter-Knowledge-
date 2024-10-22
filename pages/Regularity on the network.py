import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('./datasets/regularite-mensuelle-tgv-aqst.csv', delimiter=';')

df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Visualization 1: Trend of Average Arrival Delays
df['year_month'] = df['date'].dt.to_period('M')
monthly_delays = df.groupby('year_month')['retard_moyen_arrivee'].mean().reset_index()

# Convert 'year_month' to string to avoid serialization issues
monthly_delays['year_month'] = monthly_delays['year_month'].astype(str)

st.title("TGV Regularity Over the Years")

st.subheader("Average Arrival Delay Over Time")
fig1 = px.line(monthly_delays, x='year_month', y='retard_moyen_arrivee',
               labels={'year_month': 'Year-Month', 'retard_moyen_arrivee': 'Average Delay (minutes)'},
               title="Average Arrival Delay Over Time")
st.plotly_chart(fig1)

# Visualization 2: Lines with Most Incidents
line_incidents = df.groupby(['gare_depart', 'gare_arrivee']).agg({
    'nb_annulation': 'sum',
    'nb_train_depart_retard': 'sum',
    'nb_train_retard_arrivee': 'sum'
}).reset_index()

# Calculate the total number of incidents (cancellations + delays)
line_incidents['total_incidents'] = line_incidents['nb_annulation'] + line_incidents['nb_train_depart_retard'] + line_incidents['nb_train_retard_arrivee']

top_lines = line_incidents.nlargest(10, 'total_incidents').sort_values(by='total_incidents', ascending=True)

st.subheader("Top 10 Train Lines with the Most Incidents")
fig2 = px.bar(top_lines,
              x='total_incidents',
              y=top_lines['gare_depart'] + ' -> ' + top_lines['gare_arrivee'],
              labels={'total_incidents': 'Total Incidents', 'y': 'Train Line'},
              title="Top 10 Train Lines with the Most Incidents",
              orientation='h')

# Reverse the y-axis order
fig2.update_layout(yaxis={'categoryorder':'total ascending'})

# Display the chart
st.plotly_chart(fig2)


# Visualization 3: Causes of Delays
cause_columns = [
    'prct_cause_externe', 'prct_cause_infra', 'prct_cause_gestion_trafic',
    'prct_cause_materiel_roulant', 'prct_cause_gestion_gare', 'prct_cause_prise_en_charge_voyageurs'
]
avg_causes = df[cause_columns].mean()

st.subheader("Average Causes of Train Delays")
causes_data = pd.DataFrame({
    'Cause': avg_causes.index.str.replace('prct_cause_', '').str.replace('_', ' ').str.capitalize(),
    'Percentage': avg_causes.values
})

fig3 = px.pie(causes_data, names='Cause', values='Percentage',
              title="Average Causes of Train Delays",
              hole=0.3)
st.plotly_chart(fig3)
