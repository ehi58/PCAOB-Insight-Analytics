import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# 3.1 Import libraries
# Already done above.

# 3.2 Page configuration
st.set_page_config(
    page_title="PCAOB Inspection Dashboard",
    page_icon="data/2020-PCAOB-Logo_new.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3.3 Load data
# Load your CSV data
df = pd.read_csv('final_transformed_data.csv')

# Preprocess the data
df['Inspection Year'] = df['Inspection Year'].astype(str)

# Round float values to the nearest thousandths
float_columns = df.select_dtypes(include=['float64']).columns
df[float_columns] = df[float_columns].round(3)

# 3.4 Add a sidebar
with st.sidebar:
    st.title('📊 PCAOB Inspection Dashboard')

    selected_years = st.multiselect('Select years', options=sorted(df['Inspection Year'].unique()), default=sorted(df['Inspection Year'].unique()))
    
    selected_countries = st.multiselect('Select countries', options=sorted(df['Country'].unique()), default=sorted(df['Country'].unique()))

    selected_companies = st.multiselect('Select companies', options=sorted(df['Company'].unique()), default=sorted(df['Company'].unique()))

    color_theme_list = ['viridis', 'cividis', 'blues', 'reds']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

    word_count_min = int(df['word_count'].min())
    word_count_max = int(df['word_count'].max())
    selected_word_count = st.slider('Select word count range', min_value=word_count_min, max_value=word_count_max, value=(word_count_min, word_count_max))

# Filter the dataframe based on sidebar selections
df_filtered = df.copy()

if selected_years:
    df_filtered = df_filtered[df_filtered['Inspection Year'].isin(selected_years)]

if selected_countries:
    df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

if selected_companies:
    df_filtered = df_filtered[df_filtered['Company'].isin(selected_companies)]

df_filtered = df_filtered[(df_filtered['word_count'] >= selected_word_count[0]) & (df_filtered['word_count'] <= selected_word_count[1])]

# 3.4b Calculate key metrics
total_clients = df_filtered['Total Issuer Audit Clients'].sum()
avg_sentiment = df_filtered['sentiment_avg'].mean().round(2)
avg_word_count = df_filtered['word_count'].mean().round(2)

# 3.4c Display scorecards
st.title('PCAOB Inspection Data Dashboard')

col1, col2, col3 = st.columns(3)
col1.metric("Total Issuer Audit Clients", f"{total_clients}")
col2.metric("Average Sentiment", f"{avg_sentiment}")
col3.metric("Average Word Count", f"{avg_word_count}")

# 3.5 Plot and chart types

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
    y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Company", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
    x=alt.X(f'{input_x}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=-45)),  # Tilted labels
    color=alt.Color(f'max({input_color}):Q',
                    legend=None,
                    scale=alt.Scale(scheme=input_color_theme)),
    stroke=alt.value('black'),
    strokeWidth=alt.value(0.25),
    ).properties(width=1500, height=500)  # Wider heatmap
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="country names",
                           color_continuous_scale=input_color_theme,
                           range_color=(0, max(df_filtered['Total Issuer Audit Clients'])),
                           scope="world",  # Global scope
                           labels={'Total Issuer Audit Clients':'Total Issuer Audit Clients'}
                          )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Line chart for sentiment analysis
def make_line_chart(input_df):
    line_chart = alt.Chart(input_df).mark_line(point=True).encode(
        x='Inspection Year',
        y=alt.Y('mean(sentiment_avg)', scale=alt.Scale(domain=[0.85, 1.0])),
        color='Company'
    ).properties(
        title='Average Sentiment by Year'
    )
    return line_chart

# Word count plot
def make_word_count_plot(input_df):
    # Calculate the average word count rounded to three decimal places
    input_df['mean_word_count'] = input_df.groupby('Company')['word_count'].transform('mean').round(2)
    
    word_count_plot = alt.Chart(input_df).mark_bar().encode(
        x=alt.X('mean_word_count:Q', title='Average Word Count', axis=alt.Axis(format=".2f")),  # Ensure x-axis values are rounded to three decimal places
        y=alt.Y('Company:N', sort='-x', title='Company'),
        color='Country:N'
    ).properties(
        title='Average Word Count by Company'
    ).configure_axis(
        grid=False,
        titleFontSize=14,
        labelFontSize=12
    ).configure_view(
        strokeWidth=0
    )
    return word_count_plot

# 3.6 App layout
#st.title('PCAOB Inspection Data Dashboard')

col1, col2 = st.columns((2, 3))

with col1:
    st.markdown('#### Heatmap of Sentiment Scores by Year and Company')
    heatmap = make_heatmap(df_filtered, 'Company', 'Inspection Year', 'sentiment_avg', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

with col2:
    st.markdown('#### Choropleth Map of Total Issuer Audit Clients')
    choropleth = make_choropleth(df_filtered, 'Country', 'Total Issuer Audit Clients', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

st.markdown('#### Average Sentiment Over the Years')
line_chart = make_line_chart(df_filtered)
st.altair_chart(line_chart, use_container_width=True)

st.markdown('#### Average Word Count by Company')
word_count_plot = make_word_count_plot(df_filtered)
st.altair_chart(word_count_plot, use_container_width=True)

# Additional plots (word_count, etc.) can be added similarly.