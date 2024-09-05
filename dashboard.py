import streamlit as st
#import seaborn as sns
import pandas as pd
import altair as alt
import plotly.express as px
import os
import re

# 3.1 Import libraries
# Already done above.

# Get the port from the environment variable
port = int(os.environ.get("PORT", 8501))

# Run the app with the specified port
#st.set_option('server.port', port)

# 3.2 Page configuration
st.set_page_config(
    page_title="PCAOB Inspection Dashboard",
    page_icon="data/2020-PCAOB-Logo_new.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3.3 Load data
# Reading the Parquet file in dashboard.py because csv file was too large for GitHub.
df = pd.read_parquet('final_transformed_data_compressed.parquet', engine='pyarrow')

# Preprocess the data
df['Inspection Year'] = df['Inspection Year'].astype(str)
df['Part I.A Deficiency Rate'] = df['Part I.A Deficiency Rate'].str.replace('%', '').astype(float)

#Replace the certain values in the 'Company' column that are years to 'Non-Global Network Company' values
# List of valid inspection years
inspection_years = [str(year) for year in range(2000, 2035)]  # Adjust the range based on your data

# Replace inspection years with 'Non-Global Network Company'
df['Company'] = df['Company'].apply(
    lambda x: 'Non-Global Network Company' if x in inspection_years else x
)


# Round float values to the nearest thousandths
float_columns = df.select_dtypes(include=['float64']).columns
df[float_columns] = df[float_columns].round(3)

# 3.4 Add a sidebar
with st.sidebar:
    st.title('📊 PCAOB Inspection Report Tool Dashboard')

    st.sidebar.subheader("Project Description")
    description = """
    The Public Company Accounting Oversight Board (PCAOB) is responsible for overseeing the audits of public companies and registered audit firms(Global Network companies), 
    ensuring compliance with PCAOB standards, regulations, and other relevant professional criteria.\n
    This dashboard provides a visual representation of data extracted from PCAOB inspection reports,
    focusing on key metrics such as sentiment analysis and audit deficiency rates, offering insights into audit quality and adherence to regulatory standards.\n

    - **Sentiment Analysis**: Evaluates the tone of the language used in the inspection reports, categorizing them as positive, neutral, or negative.
    - **Deficiency Rates**: Tracks the percentage of audit engagements with significant deficiencies across different years and firms.
    - **Key Insights**: A correlation between negative sentiment scores and higher deficiency rates suggests a relationship between the report's tone and the severity of audit issues.

    Explore the data further by accessing the [PCAOB Firm Inspection Report Tool](https://pcaobus.org/oversight/inspections/firm-inspection-reports?pg={}&mpp=96&globalnetworks=Ernst%20%26%20Young%20Global%20Limited%2CDeloitte%20Touche%20Tohmatsu%20Limited%2CKPMG%20International%20Cooperative%2CPricewaterhouseCoopers%20International%20Limited&country=South%20Korea%2CSouth%20Africa%2CJapan%2CColombia%2CCayman%20Islands%2CCanada%2CBrazil%2CBahamas%2CArgentina%2CUnited%20Kingdom%2CUnited%20States%2CTaiwan%2CSwitzerland%2CSweden%2CSpain%2CLuxembourg%2CNetherlands%2CNorway%2CPanama%2CPeru%2CPhilippines%2CSingapore).
    \n
    Please feel free to reach out to me via [LinkedIn](https://www.linkedin.com/in/ehi-eromosele/)\n
    Or email me at eromosele.ehi@gmail.com
    """
    st.sidebar.write(description)
    # Add a separator line or space
    st.markdown("---")  # This adds a horizontal line for separation.
    st.title("Filters")

    # Sidebar filter for users to reintroduce 'Non-Global Network Company'
    reintroduce_non_global = st.sidebar.checkbox('Show Non-Global Network Companies.\n\n (Warning! - Some plots might crash out if other data is not filtered out or vice versa.)', value=False) # Target US and Canada and filter out other countries.

    # Filters
    # Inspection Type Filter
    with st.expander("Select Inspection Type"):
        # Text input for search functionality (support multiple search terms separated by comma or space)
        inspection_type_input = st.text_input("Type to search Inspection Type (you can separate search terms with a comma)", value="")
        
        # Split the input string by comma, space, or semicolon into search terms
        search_terms = [term.strip().lower() for term in re.split(r'[,\s;]+', inspection_type_input) if term]
        
        # Filter options based on whether any search term is in the inspection type
        if search_terms:
            filtered_inspection_types = sorted([x for x in df['Inspection Type'].unique() if any(term in x.lower() for term in search_terms)])
        else:
            filtered_inspection_types = sorted(df['Inspection Type'].unique())
        
        # Multiselect dropdown with filtered options
        selected_inspection_type = st.multiselect(
            'Select Inspection Type',
            options=filtered_inspection_types,
            default=filtered_inspection_types,
            help="Type in the inspection type to search and filter."
        )

    # Years Filter
    with st.expander("Select Years"):
        years_input = st.text_input("Type to search Years (you can separate search terms with a comma)", value="")
        search_terms = [term.strip().lower() for term in re.split(r'[,\s;]+', years_input) if term]
        
        # Convert years to strings before filtering
        if search_terms:
            filtered_years = sorted([x for x in df['Inspection Year'].unique() if any(term in str(x).lower() for term in search_terms)])
        else:
            filtered_years = sorted(df['Inspection Year'].unique())
        
        selected_years = st.multiselect(
            'Select Years',
            options=filtered_years,
            default=filtered_years,
            help="Type in the year to search and filter."
        )

    # Countries Filter
    with st.expander("Select Countries"):
        countries_input = st.text_input("Type to search Countries (you can separate search terms with a comma)", value="")
        search_terms = [term.strip().lower() for term in re.split(r'[,\s;]+', countries_input) if term]
        
        # Filter countries
        if search_terms:
            filtered_countries = sorted([x for x in df['Country'].unique() if any(term in x.lower() for term in search_terms)])
        else:
            filtered_countries = sorted(df['Country'].unique())
        
        selected_countries = st.multiselect(
            'Select Countries',
            options=filtered_countries,
            default=filtered_countries,
            help="Type in the country name to search and filter."
        )

    # Global Networks Filter
    with st.expander("Select Global Networks"):
        if not reintroduce_non_global:
            df = df[df['Company'] != 'Non-Global Network Company']
        
        global_network_input = st.text_input("Type to search Global Networks (you can separate search terms with a comma)", value="")
        search_terms = [term.strip().lower() for term in re.split(r'[,\s;]+', global_network_input) if term]
        
        # Filter global network companies
        if search_terms:
            filtered_companies = sorted([x for x in df['Company'].unique() if any(term in x.lower() for term in search_terms)])
        else:
            filtered_companies = sorted(df['Company'].unique())
        
        selected_companies = st.multiselect(
            'Select Global Network',
            options=filtered_companies,
            default=filtered_companies,
            help="Type in the global network name to search and filter."
        )

    # Firm Names Filter
    with st.expander("Select Firm Names"):
        firm_names_input = st.text_input("Type to search Firm Names (you can separate search terms with a comma)", value="")
        search_terms = [term.strip().lower() for term in re.split(r'[,\s;]+', firm_names_input) if term]
        
        # Filter firm names
        if search_terms:
            filtered_firms = sorted([x for x in df['Inspection Report Company'].unique() if any(term in x.lower() for term in search_terms)])
        else:
            filtered_firms = sorted(df['Inspection Report Company'].unique())
        
        selected_firms = st.multiselect(
            'Select Firm Names',
            options=filtered_firms,
            default=filtered_firms,
            help="Type in the firm name to search and filter."
        )

    #Add a slider filter for Total Issuer Audit Clients
    with st.expander("Total Issuer Audit Clients Range"):
        total_issuer_audit_client_count_min = 0
        total_issuer_audit_client_count_max = int(df['Total Issuer Audit Clients'].max())
        selected_total_issuer_audit_client_count = st.slider('Select range for Total Issuer Audit Clients', min_value=total_issuer_audit_client_count_min, max_value=total_issuer_audit_client_count_max, value=(total_issuer_audit_client_count_min, total_issuer_audit_client_count_max))

    #Add a slider filter for Total Audits Reviewed
    with st.expander("Total Audits Reviewed Range"):
        total_audit_reviewed_count_min = int(df['Audits Reviewed'].min())
        total_audit_reviewed_count_max = int(df['Audits Reviewed'].max())
        selected_total_audit_reviewed_count = st.slider('Select range for Total Audits Reviewed', min_value=total_audit_reviewed_count_min, max_value=total_audit_reviewed_count_max, value=(total_audit_reviewed_count_min, total_audit_reviewed_count_max))

    #Add a slider filter for Total Issuer Audit Clients
    with st.expander("Part I.A Deficiency Rate Range"):
        deficiency_rate_count_min = df['Part I.A Deficiency Rate'].min()
        deficiency_rate_count_max = df['Part I.A Deficiency Rate'].max()
        selected_deficiency_rate_count = st.slider('Select range for Deficiency Rate Range', min_value=deficiency_rate_count_min, max_value=deficiency_rate_count_max, value=(deficiency_rate_count_min, deficiency_rate_count_max))

    #Add a slider filter for word count
    with st.expander("Word Count Range"):
        word_count_min = int(df['word_count'].min())
        word_count_max = int(df['word_count'].max())
        selected_word_count = st.slider('Select word count range', min_value=word_count_min, max_value=word_count_max, value=(word_count_min, word_count_max))

    # Add a slider filter for document_sentiment_score, rounded to the nearest hundredths
    with st.expander("Sentiment Score Range"):
        sentiment_min = round(df['document_sentiment_score'].min(), 2)
        sentiment_max = round(df['document_sentiment_score'].max(), 2)
        selected_sentiment_range = st.slider('Select sentiment score range', min_value=sentiment_min, max_value=sentiment_max, value=(sentiment_min, sentiment_max))

    color_theme_list = ['viridis', 'cividis', 'blues', 'reds', 'plasma', 'inferno']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


# Filter the dataframe based on sidebar selections
df_filtered = df.copy()

# Initial filter based on a certain criteria to reduce data size

if selected_inspection_type:
    df_filtered = df_filtered[df_filtered['Inspection Type'].isin(selected_inspection_type)]

if selected_years:
    df_filtered = df_filtered[df_filtered['Inspection Year'].isin(selected_years)]

if selected_countries:
    df_filtered = df_filtered[df_filtered['Country'].isin(selected_countries)]

if selected_companies:
    df_filtered = df_filtered[df_filtered['Company'].isin(selected_companies)]

df_filtered = df_filtered[(df_filtered['Total Issuer Audit Clients'] >= selected_total_issuer_audit_client_count[0]) & (df_filtered['Total Issuer Audit Clients'] <= selected_total_issuer_audit_client_count[1])]

df_filtered = df_filtered[(df_filtered['Audits Reviewed'] >= selected_total_audit_reviewed_count[0]) & (df_filtered['Audits Reviewed'] <= selected_total_audit_reviewed_count[1])]

df_filtered = df_filtered[(df_filtered['Part I.A Deficiency Rate'] >= selected_deficiency_rate_count[0]) & (df_filtered['Part I.A Deficiency Rate'] <= selected_deficiency_rate_count[1])]

df_filtered = df_filtered[(df_filtered['word_count'] >= selected_word_count[0]) & (df_filtered['word_count'] <= selected_word_count[1])]

#Filtered data
# Remove the "%" sign and convert the "Part I.A Deficiency Rate" column to float
#df_filtered['Part I.A Deficiency Rate'] = df_filtered['Part I.A Deficiency Rate'].str.replace('%', '').astype(float)

# Replace NaN values in the 'Total Issuer Audit Clients' column with 0 and convert to float
df_filtered['Total Issuer Audit Clients'] = df_filtered['Total Issuer Audit Clients'].fillna(0).astype(float)
#df['Total Issuer Audit Clients'] = df['Total Issuer Audit Clients'].fillna(0)
#df_filtered = df[(df['Inspection Year'].isin(selected_years)) & (df['Company'].isin(selected_companies))]
df_filtered['Total Issuer Audit Clients'].fillna(0, inplace=True)

# Apply document_sentiment_score filter
df_filtered = df_filtered[(df_filtered['document_sentiment_score'] >= selected_sentiment_range[0]) & (df_filtered['document_sentiment_score'] <= selected_sentiment_range[1])]

# 3.4b Calculate key metrics
total_clients = df_filtered['Total Issuer Audit Clients'].sum()
avg_sentiment = df_filtered['document_sentiment_score'].mean()
avg_word_count = df_filtered['word_count'].mean()

# Check if total_clients is NaN or None, and handle accordingly
if pd.isna(total_clients):
    total_clients_display = "No data available"
else:
    total_clients_display = total_clients

# Check if avg_sentiment is NaN or None, and handle accordingly
if pd.isna(avg_sentiment):
    avg_sentiment_display = "No data available"
    st.write(f"**Try clicking Show Non-Global Network Companies**")
else:
    avg_sentiment_display = round(avg_sentiment, 2)

# Check if avg_word_count is NaN or None, and handle accordingly
if pd.isna(avg_word_count):
    avg_word_count_display = "No data available"
    st.write(f"**Try clicking Show Non-Global Network Companies**")
else:
    avg_word_count_display = round(avg_word_count, 2)

# Display avg_sentiment_display in the dashboard
#st.write(f"Average Sentiment: {avg_sentiment_display}")

# 3.4c Display scorecards
st.title('PCAOB Inspection Data Dashboard')

col1, col2, col3 = st.columns(3)
col1.metric("Total Issuer Audit Clients", f"{total_clients_display}")
col2.metric("Average Sentiment", f"{avg_sentiment_display}")
col3.metric("Average Word Count", f"{avg_word_count_display}")

# 3.5 Plot and chart types

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
    y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Company", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
    x=alt.X(f'{input_x}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=-45)),  # Tilted labels
    color=alt.Color(f'max({input_color}):Q',
                        legend=alt.Legend(title=input_color, orient="right"),  # Add legend for the color scale
                        scale=alt.Scale(scheme=input_color_theme)),
    stroke=alt.value('black'),
    strokeWidth=alt.value(0.25),
    ).properties(width=1500, height=500)  # Wider heatmap
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, 
                               locations=input_id, 
                               color=input_column,
                               locationmode="country names",
                               color_continuous_scale=input_color_theme,
                               range_color=(input_df[input_column].min(), input_df[input_column].max()),
                               scope="world",
                               labels={'Total Issuer Audit Clients':'Total Issuer Audit Clients'})
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
        x=alt.X('Inspection Year', axis=alt.Axis(labelAngle=-45)),  # Tilt x-axis labels by 45 degrees
        y=alt.Y('mean(document_sentiment_score)', scale=alt.Scale(domain=[0.85, 1.0])),
        color='Company'
    )
    return line_chart

# Line chart for deficiency rate
def make_line_chart2(input_df):
    line_chart2 = alt.Chart(input_df).mark_line(point=True).encode(
        x=alt.X('Inspection Year:O', axis=alt.Axis(labelAngle=-45)),  # Tilt x-axis labels by 45 degrees
        y=alt.Y('Part I.A Deficiency Rate:Q', axis=alt.Axis(title="Part I.A Deficiency Rate (%)")),
        color='Company:N'
    )
    return line_chart2

# Word count plot
def make_word_count_plot(input_df):
    # Calculate the average word count rounded to three decimal places
    input_df['mean_word_count'] = input_df.groupby('Company')['word_count'].transform('mean').round(2)
    
    word_count_plot = alt.Chart(input_df).mark_bar().encode(
        x=alt.X('mean_word_count:Q', title='Average Word Count', axis=alt.Axis(format=".2f")),  # Ensure x-axis values are rounded to three decimal places
        y=alt.Y('Company:N', sort='-x', title='Company'),
        color='Country:N'
    ).configure_axis(
        grid=False,
        titleFontSize=14,
        labelFontSize=12
    ).configure_view(
        strokeWidth=0
    )
    return word_count_plot
#-------------------------------------------------------------------------------------
# 3.6 App layout
#st.title('PCAOB Inspection Data Dashboard')

# col1, col2 = st.columns((2, 3))

# with col1:
#     st.markdown('#### Heatmap of Sentiment Scores by Year and Company')
#     heatmap = make_heatmap(df_filtered, 'Company', 'Inspection Year', 'document_sentiment_score', selected_color_theme)
#     st.altair_chart(heatmap, use_container_width=True)

# with col2:
#     st.markdown('#### Choropleth Map of Total Issuer Audit Clients')
#     choropleth = make_choropleth(df_filtered, 'Country', 'Total Issuer Audit Clients', selected_color_theme)
#     st.plotly_chart(choropleth, use_container_width=True)

# st.markdown('#### Average Sentiment Over the Years')
# line_chart = make_line_chart(df_filtered)
# st.altair_chart(line_chart, use_container_width=True)

# st.markdown('#### Average Word Count by Company')
# word_count_plot = make_word_count_plot(df_filtered)
# st.altair_chart(word_count_plot, use_container_width=True)

#-------------------------------------------------------------------------------------
#Renaming legend names/columns Company to Global Network and Inspection Report Company to Firm Names
df_filtered['Firm Names'] = df_filtered['Inspection Report Company']
df_filtered['Global Network Company'] = df_filtered['Company']

#Aggregated Metrics for Choropleth Map
df_aggregated = df_filtered.groupby('Country')['Total Issuer Audit Clients'].sum().reset_index()
df_aggregated1 = df_filtered.groupby(['Inspection Year', 'Company'], as_index=False)['Part I.A Deficiency Rate'].mean()

# First Row: Heatmap
st.markdown('#### Heatmap of Sentiment Scores by Year and Global Network Company')
st.markdown("This heatmap shows the average sentiment scores over the years for each Global Network Company. "
            "Darker colors represent more negative sentiments, while lighter colors represent more positive sentiments. The color scale on the right side of the plot "
    "indicates the exact sentiment score range.")
heatmap = make_heatmap(df_filtered, 'Company', 'Inspection Year', 'document_sentiment_score', selected_color_theme)
st.altair_chart(heatmap, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Second Row: Choropleth Map
st.markdown('#### Choropleth Map of Total Issuer Audit Clients')
st.markdown("This choropleth map displays the distribution of total issuer audit clients by country. "
            "The color intensity on the map indicates the number of audit clients in each country, "
    "with a darker color representing a higher number of clients. The color scale on the right side of the plot "
    "provides the exact range of audit clients.")
choropleth = make_choropleth(df_aggregated, 'Country', 'Total Issuer Audit Clients', selected_color_theme)
st.plotly_chart(choropleth, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

st.markdown(
    "#### Average Sentiment by Year\n"
    "This line chart visualizes the average sentiment score over the years across different companies. "
    "Each line represents a global network company, and the chart helps identify trends in sentiment over time."
)
line_chart = make_line_chart(df_filtered)
st.altair_chart(line_chart, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

st.markdown(
    "#### Average Part I.A Deficiency Rate by Year and Company\n"
    "This line chart visualizes the average Part I.A Deficiency Rate over the years across different companies. "
    "Each line represents a global network company, and the chart helps identify trends in deficiency rate over time."
)
line_fig = px.line(
    df_aggregated1,
    x='Inspection Year',
    y='Part I.A Deficiency Rate',
    color='Company',
    markers=True
)

st.plotly_chart(line_fig, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

st.markdown(
    "#### Average Word Count by Global Network Company\n"
    "This plot shows the average word count of audit reports for each Global Network Company. "
    "It provides insight into the typical length of reports produced by different companies, "
    "which could reflect the complexity or thoroughness of the audits. Higher word counts might indicate more detailed reports."
)
word_count_plot = make_word_count_plot(df_filtered)
st.altair_chart(word_count_plot, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Additional plots (word_count, etc.) can be added similarly(added later).
# Pie Chart: Distribution of Total Issuer Audit Clients by Company
#st.subheader('Distribution of Total Issuer Audit Clients by Company')
st.markdown(
    "#### Distribution of Total Issuer Audit Clients by Global Network Company\n"
    "This pie chart shows the distribution of total issuer audit clients among different companies. "
    "It provides a visual breakdown of how audit clients are distributed across companies."
)
fig_pie = px.pie(df_filtered, names='Company', values='Total Issuer Audit Clients')
st.plotly_chart(fig_pie, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Bar Chart: Total Issuer Audit Clients by Country and Company
#st.subheader('Total Issuer Audit Clients by Country and Company')
st.markdown(
    "#### Total Issuer Audit Clients by Country and Global Network Company\n"
    "This bar chart presents the total number of issuer audit clients for each company, categorized by country. "
    "The chart provides insight into the geographic distribution of audit clients among different companies."
)
fig_bar = px.bar(df_filtered, x='Country', y='Total Issuer Audit Clients', color='Global Network Company', barmode='group')
# Update the layout to tilt the x-axis labels
fig_bar.update_xaxes(tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.


# Scatter Plot: Total Issuer Audit Clients vs. Part I.A Deficiency Rate
#st.subheader('Total Issuer Audit Clients vs. Part I.A Deficiency Rate')
st.markdown(
    "#### Total Issuer Audit Clients vs. Part I.A Deficiency Rate\n"
    "This scatter plot compares the total number of issuer audit clients with the Part I.A Deficiency Rate for each Global Network Company. "
    "The plot helps identify any correlation between the number of clients and the deficiency rates."
)
fig_scatter = px.scatter(df_filtered, x='Total Issuer Audit Clients',
                         y='Part I.A Deficiency Rate', color='Global Network Company',
                         size='Total Issuer Audit Clients',
                         hover_data={
                            'Inspection Year': True,
                            'Country': True,
                            'Audits Reviewed': True,
                            'Inspection Report Date': True,
                            'Global Network Company': True
                        }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Scatter Plot: Total Sentiment Average vs. Part I.A Deficiency Rate
#st.subheader('Total Sentiment Average vs. Part I.A Deficiency Rate')
st.markdown(
    "#### Sentiment Score vs. Part I.A Deficiency Rate\n"
    "This scatter plot compares the sentiment score for each document with the Part I.A Deficiency Rate for each Global Network Company or Country. "
    "The size of each point indicates the magnitude of sentiment scores, while the position shows the relationship between sentiment and deficiency rates."
)
fig_scatter_1 = px.scatter(df_filtered, x='document_sentiment_score', 
                           y='Part I.A Deficiency Rate', color='Firm Names', 
                           size='document_sentiment_score',
                           hover_data={
                            'Inspection Year': True,
                            'Country': True,
                            'Audits Reviewed': True,
                            'Inspection Report Date': True,
                            'Global Network Company': True
                        }
)
st.plotly_chart(fig_scatter_1, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Bar Chart: Total Issuer Audit Clients by Inspection Year and Company
#st.subheader('Total Issuer Audit Clients by Inspection Year and Company')
st.markdown(
    "#### Total Issuer Audit Clients by Inspection Year and Global Network Company\n"
    "This bar chart displays the total number of issuer audit clients for each Global Network Company, broken down by inspection year. "
    "It highlights trends over time and allows for comparison between companies."
)
fig_bar_year = px.bar(df_filtered, x='Inspection Year', y='Total Issuer Audit Clients', color='Global Network Company')
st.plotly_chart(fig_bar_year, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Box Plot: Sentiment Average Distribution by Company
#st.subheader('Sentiment Average Distribution by Company')
st.markdown(
    "#### Sentiment Average Distribution by Global Network Company\n"
    "This box plot shows the distribution of sentiment averages for each Global Network Company. "
    "The box represents the interquartile range (IQR), the line inside the box represents the median, "
    "and the whiskers show the range of the data."
)
fig_box_sentiment = px.box(df_filtered, x='Company', y='document_sentiment_score', color='Global Network Company')
st.plotly_chart(fig_box_sentiment, use_container_width=True)

# Add a separator line or space
st.markdown("---")  # This adds a horizontal line for separation.

# Histogram: Distribution of Word Count by Company
#st.subheader('Distribution of Word Count by Company')
st.markdown(
    "#### Distribution of Word Count by Global Network Company\n"
    "This histogram illustrates the distribution of word counts in audit reports across different companies. "
    "It helps identify how word counts vary among companies, indicating differences in report length."
)
fig_hist_word_count = px.histogram(df_filtered, x='word_count', color='Global Network Company')
st.plotly_chart(fig_hist_word_count, use_container_width=True)

# Create a new column with hyperlinks
df_filtered['pdf_link_hyperlink'] = df_filtered['pdf_link'].apply(lambda x: f'<a href="{x}" target="_blank">data source - pdf</a>')


# Add an additional table below to manually allow users to click on the PDF link
st.write("You can click on the PDF links below for more details:")

# Display a clickable table with Inspection Year, Company, and PDF links
st.write(df_filtered[['pdf_link_hyperlink', 'Inspection Report Date', 'Inspection Year', 'Inspection Type', 'Part I.A Deficiency Rate', 'Country', 'Global Network Company', 'Firm Names', 'document_sentiment_score']].to_html(escape=False, index=False), unsafe_allow_html=True)