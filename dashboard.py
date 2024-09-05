import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import base64
from collections import Counter
import re

# Set the path for the database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indian_railway_complaints.db')

# Set page config
st.set_page_config(page_title="Indian Railway Complaints Dashboard", layout="wide")

# Custom CSS for icons
st.markdown("""
<style>
.icon {
    width: 20px;
    height: 20px;
    margin-right: 5px;
    vertical-align: middle;
}
.share-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: #1f77b4;
    font-weight: bold;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Function to load data
def load_data():
    if not os.path.exists(DB_PATH):
        st.error(f"Database file not found at {DB_PATH}. Please run the main.py script first to create the database and submit some complaints.")
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the complaints table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='complaints'")
    if not cursor.fetchone():
        st.error("The complaints table does not exist in the database. Please run the main.py script first to create the table and submit some complaints.")
        conn.close()
        return pd.DataFrame()

    # If the table exists, load the data
    df = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()

    if df.empty:
        st.warning("No complaints have been submitted yet. The dashboard will update once complaints are added.")
    else:
        df['complaint_date'] = pd.to_datetime(df['complaint_date'])
        df['complaint_resolved'] = df['complaint_resolved'].astype(bool)
    
    return df

# Function for auto-refresh
def auto_refresh():
    placeholder = st.empty()
    while True:
        placeholder.text("Refreshing data...")
        time.sleep(5)  # Wait for 5 seconds
        placeholder.empty()
        st.experimental_rerun()

# Function to generate a shareable link
def generate_share_link(complaint):
    complaint_data = f"Category: {complaint['complaint_category']}\n"
    complaint_data += f"Date: {complaint['complaint_date'].date()}\n"
    complaint_data += f"Description: {complaint['complaint_description']}\n"
    complaint_data += f"Resolved: {'Yes' if complaint['complaint_resolved'] else 'No'}\n"
    complaint_data += f"Station: {complaint['station']}\n"
    complaint_data += f"Seat Number: {complaint['seat_number']}"
    
    encoded_data = base64.b64encode(complaint_data.encode()).decode()
    return f"https://yourwebsite.com/share?data={encoded_data}"

# Main dashboard
st.markdown('<p class="big-font">Indian Railway Complaints Dashboard (AI)</p>', unsafe_allow_html=True)

# Display the database path
st.sidebar.write(f"Database path: {DB_PATH}")

# Add a refresh button
if st.sidebar.button("Refresh Data"):
    st.experimental_rerun()

# Add auto-refresh option
auto_refresh_option = st.sidebar.checkbox("Enable Auto-refresh")
if auto_refresh_option:
    auto_refresh()

data = load_data()

if not data.empty:
    # Sidebar for filtering
    st.sidebar.header('Filters')
    selected_categories = st.sidebar.multiselect(
        'Select Complaint Categories',
        options=data['complaint_category'].unique(),
        default=data['complaint_category'].unique()
    )

    date_range = st.sidebar.date_input(
        'Select Date Range',
        [data['complaint_date'].min().date(), data['complaint_date'].max().date()]
    )

    # Filter data based on selection
    filtered_data = data[
        (data['complaint_category'].isin(selected_categories)) &
        (data['complaint_date'].dt.date >= date_range[0]) &
        (data['complaint_date'].dt.date <= date_range[1])
    ]

    # Overall statistics
    st.markdown('<p class="medium-font">Overall Statistics</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric('Total Complaints', len(filtered_data))
    col2.metric('Resolution Rate', f"{filtered_data['complaint_resolved'].mean():.2%}")
    col3.metric('Average Complaint Length', f"{filtered_data['complaint_description'].str.len().mean():.0f} characters")

    # Complaint Categories Pie Chart
    st.markdown('<p class="medium-font">Complaint Categories</p>', unsafe_allow_html=True)
    category_counts = filtered_data['complaint_category'].value_counts()
    fig = px.pie(values=category_counts.values, names=category_counts.index, title='Distribution of Complaint Categories')
    st.plotly_chart(fig, use_container_width=True)

    # Resolution Rate by Category
    st.markdown('<p class="medium-font">Resolution Rate by Category</p>', unsafe_allow_html=True)
    resolution_rate = filtered_data.groupby('complaint_category')['complaint_resolved'].mean().sort_values(ascending=False)
    fig = px.bar(x=resolution_rate.index, y=resolution_rate.values, 
                 labels={'x': 'Category', 'y': 'Resolution Rate'},
                 title='Resolution Rate by Complaint Category',
                 color=resolution_rate.values,
                 color_continuous_scale='Viridis')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Complaints Over Time
    st.markdown('<p class="medium-font">Complaints Over Time</p>', unsafe_allow_html=True)
    complaints_over_time = filtered_data.groupby(filtered_data['complaint_date'].dt.to_period('M')).size().reset_index()
    complaints_over_time.columns = ['Date', 'Number of Complaints']
    complaints_over_time['Date'] = complaints_over_time['Date'].dt.to_timestamp()

    fig = px.line(complaints_over_time, x='Date', y='Number of Complaints', 
                  title='Number of Complaints Over Time',
                  line_shape='spline', render_mode='svg')
    fig.update_traces(line=dict(color='#1f77b4', width=3))
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    # Resolution Rate Over Time
    st.markdown('<p class="medium-font">Resolution Rate Over Time</p>', unsafe_allow_html=True)
    resolution_over_time = filtered_data.groupby(filtered_data['complaint_date'].dt.to_period('M'))['complaint_resolved'].mean().reset_index()
    resolution_over_time.columns = ['Date', 'Resolution Rate']
    resolution_over_time['Date'] = resolution_over_time['Date'].dt.to_timestamp()

    fig = px.line(resolution_over_time, x='Date', y='Resolution Rate', 
                  title='Resolution Rate Over Time',
                  line_shape='spline', render_mode='svg')
    fig.update_traces(line=dict(color='#2ca02c', width=3))
    fig.update_layout(hovermode='x unified', yaxis_tickformat='.0%')
    st.plotly_chart(fig, use_container_width=True)

    # Word Cloud of Complaints
   st.markdown('<p class="medium-font">Most Common Words in Complaints</p>', unsafe_allow_html=True)
text = ' '.join(filtered_data['complaint_description'])
words = re.findall(r'\w+', text.lower())
word_counts = Counter(words)
common_words = word_counts.most_common(20)  # Get the 20 most common words

# Create a bar chart of the most common words
fig = px.bar(x=[word for word, count in common_words], 
             y=[count for word, count in common_words],
             labels={'x': 'Word', 'y': 'Count'},
             title='Most Common Words in Complaints')
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

    # Sample Complaints with Share Button
    st.markdown('<p class="medium-font">Sample Complaints</p>', unsafe_allow_html=True)
    sample_complaints = filtered_data.sample(min(5, len(filtered_data)))
    for _, complaint in sample_complaints.iterrows():
        with st.expander(f"{complaint['complaint_category']} - {complaint['complaint_date'].date()}"):
            st.write(f"**Description:** {complaint['complaint_description']}")
            st.write(f"**Resolved:** {'Yes' if complaint['complaint_resolved'] else 'No'}")
            st.write(f"**Station:** {complaint['station']}")
            st.write(f"**Seat Number:** {complaint['seat_number']}")
            
            # Add share buttons with SVG icons
            share_link = generate_share_link(complaint)
            whatsapp_icon = "https://upload.wikimedia.org/wikipedia/commons/5/5e/WhatsApp_icon.png"
            email_icon = "https://akm-img-a-in.tosshub.com/businesstoday/images/story/201904/gmail-660_040119014433.jpg?size=948:533"
            
            st.markdown(f'<a class="share-link" href="https://wa.me/?text=Check%20out%20this%20railway%20complaint:%20{share_link}" target="_blank"><img class="icon" src="{whatsapp_icon}" alt="WhatsApp Icon">Share via WhatsApp</a>', unsafe_allow_html=True)
            st.markdown(f'<a class="share-link" href="mailto:?subject=Railway%20Complaint&body=Check%20out%20this%20railway%20complaint:%20{share_link}" target="_blank"><img class="icon" src="{email_icon}" alt="Email Icon">Share via Email</a>', unsafe_allow_html=True)
else:
    st.stop()
