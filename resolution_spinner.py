import random
import streamlit as st
import sqlite3
import time
import urllib.parse
from streamlit_lottie import st_lottie
import requests
import json

# Move CSS before the title and update it
st.set_page_config(page_title="Resolution Roulette", initial_sidebar_state="collapsed")


def load_lottie_animation(url):
    import requests
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

# Database functions
def init_db():
    conn = sqlite3.connect("resolutions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resolutions (
            id INTEGER PRIMARY KEY,
            category TEXT,
            resolution TEXT
        )
    """)
    conn.commit()
    conn.close()

def normalize_text(text):
    """Normalize text for comparison by converting to lowercase and removing extra punctuation"""
    return text.lower().strip().rstrip('!.,')

def get_all_resolutions():
    # Initialize with predefined resolutions
    all_resolutions = {
        "Fun": ["Take a dance class", "Go skydiving", "Start a travel blog"]
    }
    
    # Load and merge custom resolutions
    conn = sqlite3.connect("resolutions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, resolution FROM resolutions")
    custom_results = cursor.fetchall()
    conn.close()
    
    # Merge custom resolutions
    for category, resolution in custom_results:
        if category in all_resolutions:
            if resolution not in all_resolutions[category]:  # Avoid duplicates
                all_resolutions[category].append(resolution)
        else:
            all_resolutions[category] = [resolution]
    
    return all_resolutions

def add_to_db(category, resolution):
    conn = sqlite3.connect("resolutions.db")
    cursor = conn.cursor()
    
    # Check if normalized version already exists
    normalized = normalize_text(resolution)
    cursor.execute("""
        SELECT 1 FROM resolutions 
        WHERE category = ? AND LOWER(TRIM(resolution)) = ?
    """, (category, normalized))
    
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO resolutions (category, resolution) VALUES (?, ?)", 
                      (category, resolution))
        conn.commit()
        result = True
    else:
        result = False
    
    conn.close()
    return result

# Initialize database and load all resolutions
init_db()
resolutions = get_all_resolutions()

# Load Lottie animation from a file
#with open("purple_spinwheel.json", "r") as f:
 #   lottie_animation = json.load(f)

# Display the animation
#st_lottie(lottie_animation, height=300, key="spinner")

def get_random_resolution(category):
    global resolutions
    resolutions = get_all_resolutions()  # Refresh resolutions
    return random.choice(resolutions.get(category, []))

# Create a container for persistent animations
animation_container = st.container()

with animation_container:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.title("Resolution Roulette 🎉")
    with col2:
        lottie_fireworks = load_lottie_animation("https://lottie.host/2f3e9d34-f0dc-4e1e-9629-2a35124e5118/ataIYRNKyb.json")
        if lottie_fireworks:
            st_lottie(
                lottie_fireworks, 
                height=125, 
                key="fireworks",
                loop=True,
                quality="high",
                speed=1,
                reverse=False
            )


# Style the app
st.markdown(
    """
    <style>
    body {
        background-color: #f9f9f9;
        background-image: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #333333;
        font-family: 'Arial', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
#style the buttons
st.markdown(
    """
    <style>
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #4caf50, #81c784);
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #81c784, #4caf50);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# User selects a category
category = st.selectbox("Choose a category:", list(resolutions.keys()))

lottie_spinner = load_lottie_animation("https://lottie.host/b9df9c61-42a8-47aa-86b0-ad1bc4b23d96/u9EAUGM3Et.json")
if st.button("Spin the Wheel!"):
    st_lottie(
        lottie_spinner, 
        height=300, 
        key="spinner",
        loop=True,
        quality="high",
        speed=1.5
    )
    resolution = random.choice(resolutions[category])
    time.sleep(5)
    st.success(f"🎯 Your resolution: {resolution}")




# Show all resolutions for the category
with st.expander("View all resolutions in this category"):
    st.write(resolutions[category])

# Section for adding custom resolutions
st.header("Add Your Own Resolution")
custom_category = st.selectbox("Select a category for your resolution:", list(resolutions.keys()))
custom_resolution = st.text_input("Enter your resolution:")

# Modify the add resolution button handler
if st.button("Add Resolution", key="add_resolution_button"):
    if custom_resolution:
        if add_to_db(custom_category, custom_resolution):
            resolutions = get_all_resolutions()
            st.success(f"✅ Added: '{custom_resolution}' to {custom_category}")
        else:
            st.warning("This resolution already exists in this category!")
    else:
        st.error("❌ Please enter a resolution before submitting.")


#streamlit will display multiline string as markdown if not assigned to any variable
apiComment=""" 
if resolution:
    base_url = "http://your-app-url.com"
    encoded_resolution = urllib.parse.quote_plus(resolution)
    share_url = f"{base_url}/?resolution={encoded_resolution}"

    st.write("💡 Share your resolution with this link:")
    st.code(share_url)
    """
