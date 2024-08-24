
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="Enhanced PCAOB Inspection Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
df = pd.read_csv('final_transformed_data.csv')

# Preprocess the data
df['Inspection Year'] = df['Inspection Year'].astype(str)
float_columns = df.select_dtypes(include=['float64']).columns
df[float_columns] = df[float_columns].round(3)

# Convert "Part I.A Deficiency Rate" to a numeric type after removing the "%" sign
df['Part I.A Deficiency Rate'] = df['Part I.A Deficiency Rate'].str.replace('%', '').astype(float)

# Add a sidebar
st.sidebar.title('📊 Enhanced PCAOB Inspection Dashboard')

# Description section in the sidebar above the filters
st.sidebar.subheader("Project Description")
description = """
The Public Company Accounting Oversight Board (PCAOB) issues inspection reports that summarize the results of their inspections of registered public accounting firms. 
The PCAOB's inspections assess a firm's compliance with laws, rules, and professional standards, as well as their quality control system and audit work for public companies and broker-dealers. 
The PCAOB's goal is to improve audit quality and communicate their findings.

The PCAOB provides each firm with a report that summarizes any deficiencies found during the inspection. 
A portion of each report is available to the public and can be accessed with search and filtering tools. 
The public portion of the data is also available for download in CSV, XML, and JSON formats. 
The PCAOB also publishes an annual summary report that provides information on the inspections of firms with broker-dealer clients.
"""
st.sidebar.write(description)

# Add filters
selected_years = st.sidebar.multiselect('Select years', options=sorted(df['Inspection Year'].unique()), default=sorted(df['Inspection Year'].unique()))
selected_countries = st.sidebar.multiselect('Select countries', options=sorted(df['Country'].unique()), default=sorted(df['Country'].unique()))
selected_companies = st.sidebar.multiselect('Select companies', options=sorted(df['Company'].unique()), default=sorted(df['Company'].unique()))
word_count_min = int(df['word_count'].min())
word_count_max = int(df['word_count'].max())
selected_word_count = st.sidebar.slider('Select word count range', min_value=word_count_min, max_value=word_count_max, value=(word_count_min, word_count_max))

# New filter: Sentiment score (sentiment_avg)
sentiment_avg_values = sorted(df['sentiment_avg'].unique())
selected_sentiments = st.sidebar.multiselect('Select sentiment scores', options=sentiment_avg_values, default=sentiment_avg_values)

# Filter the dataframe based on sidebar selections
df_filtered = df.copy()

if selected_years:
    df_filtered = df_filtered[df_filtered['Inspection Year'].isin(selected_years)]

if selected_countries:
    df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

if selected_companies:
    df_filtered = df_filtered[df_filtered['Company'].isin(selected_companies)]

df_filtered = df_filtered[(df_filtered['word_count'] >= selected_word_count[0]) & (df_filtered['word_count'] <= selected_word_count[1])]

if selected_sentiments:
    df_filtered = df_filtered[df_filtered['sentiment_avg'].isin(selected_sentiments)]

#Filtered data
df['Total Issuer Audit Clients'] = df['Total Issuer Audit Clients'].fillna(0)
df_filtered = df[(df['Inspection Year'].isin(selected_years)) & (df['Company'].isin(selected_companies))]

# Main content layout

st.title("PCAOB Inspection Report Analysis")

# Pie Chart: Distribution of Total Issuer Audit Clients by Company
st.subheader('Distribution of Total Issuer Audit Clients by Company')
fig_pie = px.pie(df_filtered, names='Company', values='Total Issuer Audit Clients', title='Distribution of Total Issuer Audit Clients by Company')
st.plotly_chart(fig_pie)

# Bar Chart: Total Issuer Audit Clients by Country and Company
st.subheader('Total Issuer Audit Clients by Country and Company')
fig_bar = px.bar(df_filtered, x='Country', y='Total Issuer Audit Clients', color='Company', barmode='group', title='Total Issuer Audit Clients by Country and Company')
st.plotly_chart(fig_bar)

# Scatter Plot: Total Issuer Audit Clients vs. Part I.A Deficiency Rate
st.subheader('Total Issuer Audit Clients vs. Part I.A Deficiency Rate')
fig_scatter = px.scatter(df_filtered, x='Total Issuer Audit Clients', y='Part I.A Deficiency Rate', color='Company', size='Total Issuer Audit Clients', title='Total Issuer Audit Clients vs. Part I.A Deficiency Rate')
st.plotly_chart(fig_scatter)

# Bar Chart: Total Issuer Audit Clients by Inspection Year and Company
st.subheader('Total Issuer Audit Clients by Inspection Year and Company')
fig_bar_year = px.bar(df_filtered, x='Inspection Year', y='Total Issuer Audit Clients', color='Company', title='Total Issuer Audit Clients by Inspection Year and Company')
st.plotly_chart(fig_bar_year)

# Box Plot: Sentiment Average Distribution by Company
st.subheader('Sentiment Average Distribution by Company')
fig_box_sentiment = px.box(df_filtered, x='Company', y='sentiment_avg', color='Company', title='Sentiment Average Distribution by Company')
st.plotly_chart(fig_box_sentiment)

# Histogram: Distribution of Word Count by Company
st.subheader('Distribution of Word Count by Company')
fig_hist_word_count = px.histogram(df_filtered, x='word_count', color='Company', title='Distribution of Word Count by Company')
st.plotly_chart(fig_hist_word_count)
