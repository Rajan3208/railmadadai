import streamlit as st
import sqlite3
import random
import string
from datetime import datetime
import os

# Set the here path for the database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indian_railway_complaints.db')

# Function to create complaints table
def create_complaints_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id INTEGER PRIMARY KEY,
        pnr TEXT,
        complaint_date DATETIME,
        complaint_category TEXT,
        complaint_description TEXT,
        complaint_resolved BOOLEAN,
        station TEXT,
        seat_number TEXT,
        reference_number TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Function to generate a unique reference number
def generate_reference_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Function to submit a complaint
def submit_complaint(category, description, pnr, station, seat_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    reference_number = generate_reference_number()
    cursor.execute('''
    INSERT INTO complaints (pnr, complaint_date, complaint_category, complaint_description, complaint_resolved, station, seat_number, reference_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pnr, datetime.now(), category, description, False, station, seat_number, reference_number))
    conn.commit()
    conn.close()
    return reference_number

# Function to check complaint status
def check_complaint_status(ref_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE reference_number = ?", (ref_number,))
    complaint = cursor.fetchone()
    conn.close()
    return complaint

# Pre-defined complaint categories
complaint_categories = [
    "Cleanliness Concerns",
    "Train Delays",
    "Fighting/Unruly Behavior",
    "Safety Concerns",
    "Ticket Booking Issues",
    "Food Quality",
    "Staff Behavior",
    "Other"
]

# Ensure the complaints table exists
create_complaints_table()

# Streamlit app
st.set_page_config(page_title="Rail Madad Complaint Portal", page_icon="🚂", layout="wide")

# Custom CSS to make the app more stylish and add the background image
st.markdown("""
<style>
    .stApp {
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Vande_Bharat_Express_around_Mumbai.jpg/450px-Vande_Bharat_Express_around_Mumbai.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .main .block-container {
        background-color: rgba(240, 240, 245, 0.95);  /* Light grayish blue with high opacity */
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background-color: rgba(255, 255, 255, 0.95);
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        width: 100%;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        background-color: #ffffff;
        color: #1e3a8a;
        border-radius: 5px;
        border: 1px solid #d1d5db;
    }
    .quick-link {
        margin-bottom: 10px;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        padding: 5px 0;
    }
    .stAlert {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Layout
col1, col2, col3 = st.columns([2,5,2])

# Left Aside
with col1:
    st.sidebar.header("Past Complaints")
    if st.sidebar.button("View Past Complaints", key="view_past_complaints"):
        st.sidebar.write("Feature coming soon!")

# Main Content
with col2:
    st.title("🚂 Rail Madad Complaint Portal")

    # Complaint submission form
    st.header("Submit a New Complaint")

    pnr = st.text_input("PNR Number")
    station = st.text_input("Station")
    seat_number = st.text_input("Seat Number")

    selected_category = st.selectbox("Select Complaint Category", complaint_categories)
    complaint_text = st.text_area("Write your complaint here...")

    if st.button("Submit Complaint", key="submit_complaint"):
        if complaint_text.strip() != "" and pnr and station and seat_number:
            reference_number = submit_complaint(selected_category, complaint_text, pnr, station, seat_number)
            st.markdown(f"**Reference Number:** {reference_number} Check Your Status")
            st.success("Your complaint is submitted to Jaipur Junction. We will ensure that your problem gets resolved at Jaipur Junction.", icon="✅")
        else:
            st.error("Please fill in all fields before submitting.")

# Right Aside
with col3:
    st.sidebar.header("Quick Links")

    # Check Status
    st.sidebar.subheader("Check Complaint Status")
    ref_number = st.sidebar.text_input("Enter complaint reference number:")
    if st.sidebar.button("Check Status", key="check_status_sidebar"):
        complaint = check_complaint_status(ref_number)
        if complaint:
            st.sidebar.write(f"Complaint #{ref_number}:")
            st.sidebar.write(f"Category: {complaint[3]}")
            st.sidebar.write(f"Details: {complaint[4][:50]}...")
            st.sidebar.write(f"Status: {'Resolved' if complaint[5] else 'Processing'}")
        else:
            st.sidebar.write("No complaint found with this reference number.")

    # Other Quick Links
    st.sidebar.markdown("<div class='quick-link'>", unsafe_allow_html=True)
    if st.sidebar.button("Get Help", key="get_help"):
        st.sidebar.write("Help center coming soon!")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.markdown("<div class='quick-link'>", unsafe_allow_html=True)
    if st.sidebar.button("Explore Indian Railway", key="explore_railway"):
        st.sidebar.write("Railway information coming soon!")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.markdown("<div class='quick-link'>", unsafe_allow_html=True)
    if st.sidebar.button("Book Ticket", key="book_ticket"):
        st.sidebar.write("Ticket booking integration coming soon!")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Display the database path (you can remove this in production)
st.sidebar.write(f"Database path: {DB_PATH}")
