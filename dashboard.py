import streamlit as st
import seaborn as sns
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

    st.sidebar.subheader("Project Description")
    description = """
    The **Public Company Accounting Oversight Board (PCAOB)** oversees the audits of public companies and broker-dealers to ensure compliance with laws and professional standards. 
    This dashboard analyzes PCAOB inspection reports with a focus on sentiment analysis and audit deficiency rates.

    - **Sentiment Analysis**: Evaluates the tone of the language used in the inspection reports, categorizing them as positive, neutral, or negative.
    - **Deficiency Rates**: Tracks the percentage of audit engagements with significant deficiencies across different years and firms.
    - **Key Insights**: A correlation between negative sentiment scores and higher deficiency rates suggests a relationship between the report's tone and the severity of audit issues.

    Explore the data further by accessing the [data source](https://pcaobus.org/oversight/inspections/firm-inspection-reports?pg={}&mpp=96&globalnetworks=Ernst%20%26%20Young%20Global%20Limited%2CDeloitte%20Touche%20Tohmatsu%20Limited%2CKPMG%20International%20Cooperative%2CPricewaterhouseCoopers%20International%20Limited&country=South%20Korea%2CSouth%20Africa%2CJapan%2CColombia%2CCayman%20Islands%2CCanada%2CBrazil%2CBahamas%2CArgentina%2CUnited%20Kingdom%2CUnited%20States%2CTaiwan%2CSwitzerland%2CSweden%2CSpain%2CLuxembourg%2CNetherlands%2CNorway%2CPanama%2CPeru%2CPhilippines%2CSingapore).
    """
    st.sidebar.write(description)

    selected_years = st.multiselect('Select years', options=sorted(df['Inspection Year'].unique()), default=sorted(df['Inspection Year'].unique()))
    
    selected_countries = st.multiselect('Select countries', options=sorted(df['Country'].unique()), default=sorted(df['Country'].unique()))

    selected_companies = st.multiselect('Select companies', options=sorted(df['Company'].unique()), default=sorted(df['Company'].unique()))

    color_theme_list = ['viridis', 'cividis', 'blues', 'reds']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

    #Add a slider filter for word count
    word_count_min = int(df['word_count'].min())
    word_count_max = int(df['word_count'].max())
    selected_word_count = st.slider('Select word count range', min_value=word_count_min, max_value=word_count_max, value=(word_count_min, word_count_max))

    # Add a slider filter for sentiment_avg, rounded to the nearest hundredths
    sentiment_min = round(df['sentiment_avg'].min(), 2)
    sentiment_max = round(df['sentiment_avg'].max(), 2)
    selected_sentiment_range = st.sidebar.slider('Select sentiment score range', min_value=sentiment_min, max_value=sentiment_max, value=(sentiment_min, sentiment_max))



# Filter the dataframe based on sidebar selections
df_filtered = df.copy()

if selected_years:
    df_filtered = df_filtered[df_filtered['Inspection Year'].isin(selected_years)]

if selected_countries:
    df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

if selected_companies:
    df_filtered = df_filtered[df_filtered['Company'].isin(selected_companies)]

df_filtered = df_filtered[(df_filtered['word_count'] >= selected_word_count[0]) & (df_filtered['word_count'] <= selected_word_count[1])]

#Filtered data
# Remove the "%" sign and convert the "Part I.A Deficiency Rate" column to float
df_filtered['Part I.A Deficiency Rate'] = df_filtered['Part I.A Deficiency Rate'].str.replace('%', '').astype(float)

# Replace NaN values in the 'Total Issuer Audit Clients' column with 0 and convert to float
df_filtered['Total Issuer Audit Clients'] = df_filtered['Total Issuer Audit Clients'].fillna(0).astype(float)
#df['Total Issuer Audit Clients'] = df['Total Issuer Audit Clients'].fillna(0)
#df_filtered = df[(df['Inspection Year'].isin(selected_years)) & (df['Company'].isin(selected_companies))]

# Apply sentiment_avg filter
df_filtered = df_filtered[(df_filtered['sentiment_avg'] >= selected_sentiment_range[0]) & (df_filtered['sentiment_avg'] <= selected_sentiment_range[1])]

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

# Additional plots (word_count, etc.) can be added similarly(added later).
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

# Scatter Plot: Total Sentiment Sum vs. Part I.A Deficiency Rate
st.subheader('Total Sentiment Sum vs. Part I.A Deficiency Rate')
fig_scatter_1 = px.scatter(df_filtered, x='sentiment_sum', y='Part I.A Deficiency Rate', color='Company', size='sentiment_sum', title='Total Sentiment Sum vs. Part I.A Deficiency Rate')
st.plotly_chart(fig_scatter_1)

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