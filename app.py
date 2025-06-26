import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
from utils.recycle_info import recycle_guide
import pandas as pd
import os
from datetime import datetime
import folium
from streamlit_folium import folium_static
import streamlit.components.v1 as components
import plotly.express as px
import folium.plugins
# Add these imports for Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Set page config FIRST
st.set_page_config(page_title="RecycleLens", layout="wide")

# Google Sheets Setup
@st.cache_resource
def setup_google_sheets():
    # Define the scope
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # Use credentials from secrets
    try:
        # First, try to get credentials from a file
        credentials_path = "credential/jurnal-463316-2963a6576f8f.json"
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    except Exception as e:
        st.error(f"Could not load credentials from file: {e}")
        try:
            credentials_dict = st.secrets["service_account"]
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        except Exception as e:
            st.error(f"Gagal Mengambil Credentials: {e}")
            return None
    
    # Authorize the client
    client = gspread.authorize(credentials)
    
    # Define the sheet name
    SHEET_NAME = "RecycleLens_Deteksi_Sampah_Data"
    
    try:
        # Try to open the sheet
        sheet = client.open(SHEET_NAME).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        # Create a new sheet if it doesn't exist
        sheet = client.create(SHEET_NAME).sheet1
        # Set up the header row
        sheet.append_row(['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
    
    return sheet

# Initialize Google Sheet
sheet = setup_google_sheets()

# Load model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('models/DenseNet121_trashnetmerged_best_model.h5')

model = load_model()

# Kategori
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi Prediksi
def predict_image(img):
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)
    pred = model.predict(img_array)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))
    return CATEGORIES[idx], confidence

# Google Sheets Management Functions
def save_detection_to_sheets(jenis_sampah, keyakinan_model, latitude, longitude):
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, jenis_sampah, str(keyakinan_model), str(latitude), str(longitude)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def get_detection_history():
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Get all the data from the sheet
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # If the sheet is empty (only headers), return an empty DataFrame with columns
        if len(df) == 0:
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Fix column names if they don't match expected names
        if 'jenis_sampah' not in df.columns:
            # Get the actual column names
            actual_columns = df.columns.tolist()
            
            # Check if we have exactly 5 columns as expected
            if len(actual_columns) == 5:
                # Map the columns to expected names based on position
                # Assuming order is: timestamp, jenis_sampah, keyakinan_model, latitude, longitude
                expected_columns = ['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude']
                column_mapping = {actual_columns[i]: expected_columns[i] for i in range(5)}
                
                # Rename the columns
                df = df.rename(columns=column_mapping)
        
        # Convert column types
        if 'keyakinan_model' in df.columns:
            df['keyakinan_model'] = pd.to_numeric(df['keyakinan_model'], errors='coerce')
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error getting data from Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])

# Initialize Google Sheet
sheet = setup_google_sheets()

# Load model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('models/DenseNet121_trashnetmerged_best_model.h5')

model = load_model()

# Kategori
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi Prediksi
def predict_image(img):
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)
    pred = model.predict(img_array)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))
    return CATEGORIES[idx], confidence

# Google Sheets Management Functions
def save_detection_to_sheets(jenis_sampah, keyakinan_model, latitude, longitude):
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, jenis_sampah, str(keyakinan_model), str(latitude), str(longitude)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def get_detection_history():
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Get all the data from the sheet
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # If the sheet is empty (only headers), return an empty DataFrame with columns
        if len(df) == 0:
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Fix column names if they don't match expected names
        if 'jenis_sampah' not in df.columns:
            # Get the actual column names
            actual_columns = df.columns.tolist()
            
            # Check if we have exactly 5 columns as expected
            if len(actual_columns) == 5:
                # Map the columns to expected names based on position
                # Assuming order is: timestamp, jenis_sampah, keyakinan_model, latitude, longitude
                expected_columns = ['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude']
                column_mapping = {actual_columns[i]: expected_columns[i] for i in range(5)}
                
                # Rename the columns
                df = df.rename(columns=column_mapping)
        
        # Convert column types
        if 'keyakinan_model' in df.columns:
            df['keyakinan_model'] = pd.to_numeric(df['keyakinan_model'], errors='coerce')
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error getting data from Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])

# Initialize Google Sheet
sheet = setup_google_sheets()

# Load model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('models/DenseNet121_trashnetmerged_best_model.h5')

model = load_model()

# Kategori
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi Prediksi
def predict_image(img):
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)
    pred = model.predict(img_array)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))
    return CATEGORIES[idx], confidence

# Google Sheets Management Functions
def save_detection_to_sheets(jenis_sampah, keyakinan_model, latitude, longitude):
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, jenis_sampah, str(keyakinan_model), str(latitude), str(longitude)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def get_detection_history():
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Get all the data from the sheet
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # If the sheet is empty (only headers), return an empty DataFrame with columns
        if len(df) == 0:
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Fix column names if they don't match expected names
        if 'jenis_sampah' not in df.columns:
            # Get the actual column names
            actual_columns = df.columns.tolist()
            
            # Check if we have exactly 5 columns as expected
            if len(actual_columns) == 5:
                # Map the columns to expected names based on position
                # Assuming order is: timestamp, jenis_sampah, keyakinan_model, latitude, longitude
                expected_columns = ['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude']
                column_mapping = {actual_columns[i]: expected_columns[i] for i in range(5)}
                
                # Rename the columns
                df = df.rename(columns=column_mapping)
        
        # Convert column types
        if 'keyakinan_model' in df.columns:
            df['keyakinan_model'] = pd.to_numeric(df['keyakinan_model'], errors='coerce')
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error getting data from Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])

# Initialize Google Sheet
sheet = setup_google_sheets()

# Load model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('models/DenseNet121_trashnetmerged_best_model.h5')

model = load_model()

# Kategori
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi Prediksi
def predict_image(img):
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)
    pred = model.predict(img_array)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))
    return CATEGORIES[idx], confidence

# Google Sheets Management Functions
def save_detection_to_sheets(jenis_sampah, keyakinan_model, latitude, longitude):
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, jenis_sampah, str(keyakinan_model), str(latitude), str(longitude)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def get_detection_history():
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Get all the data from the sheet
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # If the sheet is empty (only headers), return an empty DataFrame with columns
        if len(df) == 0:
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Fix column names if they don't match expected names
        if 'jenis_sampah' not in df.columns:
            # Get the actual column names
            actual_columns = df.columns.tolist()
            
            # Check if we have exactly 5 columns as expected
            if len(actual_columns) == 5:
                # Map the columns to expected names based on position
                # Assuming order is: timestamp, jenis_sampah, keyakinan_model, latitude, longitude
                expected_columns = ['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude']
                column_mapping = {actual_columns[i]: expected_columns[i] for i in range(5)}
                
                # Rename the columns
                df = df.rename(columns=column_mapping)
        
        # Convert column types
        if 'keyakinan_model' in df.columns:
            df['keyakinan_model'] = pd.to_numeric(df['keyakinan_model'], errors='coerce')
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error getting data from Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])

# Initialize Google Sheet
sheet = setup_google_sheets()

# Load model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('models/DenseNet121_trashnetmerged_best_model.h5')

model = load_model()

# Kategori
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi Prediksi
def predict_image(img):
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)
    pred = model.predict(img_array)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))
    return CATEGORIES[idx], confidence

# Google Sheets Management Functions
def save_detection_to_sheets(jenis_sampah, keyakinan_model, latitude, longitude):
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, jenis_sampah, str(keyakinan_model), str(latitude), str(longitude)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def get_detection_history():
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Get all the data from the sheet
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # If the sheet is empty (only headers), return an empty DataFrame with columns
        if len(df) == 0:
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Fix column names if they don't match expected names
        if 'jenis_sampah' not in df.columns:
            # Get the actual column names
            actual_columns = df.columns.tolist()
            
            # Check if we have exactly 5 columns as expected
            if len(actual_columns) == 5:
                # Map the columns to expected names based on position
                # Assuming order is: timestamp, jenis_sampah, keyakinan_model, latitude, longitude
                expected_columns = ['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude']
                column_mapping = {actual_columns[i]: expected_columns[i] for i in range(5)}
                
                # Rename the columns
                df = df.rename(columns=column_mapping)
        
        # Convert column types
        if 'keyakinan_model' in df.columns:
            df['keyakinan_model'] = pd.to_numeric(df['keyakinan_model'], errors='coerce')
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error getting data from Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])

# Initialize Google Sheet
sheet = setup_google_sheets()

# Load model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('models/DenseNet121_trashnetmerged_best_model.h5')

model = load_model()

# Kategori
CATEGORIES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi Prediksi
def predict_image(img):
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)
    pred = model.predict(img_array)
    idx = np.argmax(pred)
    confidence = float(np.max(pred))
    return CATEGORIES[idx], confidence

# Google Sheets Management Functions
def save_detection_to_sheets(jenis_sampah, keyakinan_model, latitude, longitude):
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, jenis_sampah, str(keyakinan_model), str(latitude), str(longitude)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def get_detection_history():
    try:
        if sheet is None:
            st.error("Google Sheets connection not available")
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Get all the data from the sheet
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # If the sheet is empty (only headers), return an empty DataFrame with columns
        if len(df) == 0:
            return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
        
        # Fix column names if they don't match expected names
        if 'jenis_sampah' not in df.columns:
            # Get the actual column names
            actual_columns = df.columns.tolist()
            
            # Check if we have exactly 5 columns as expected
            if len(actual_columns) == 5:
                # Map the columns to expected names based on position
                # Assuming order is: timestamp, jenis_sampah, keyakinan_model, latitude, longitude
                expected_columns = ['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude']
                column_mapping = {actual_columns[i]: expected_columns[i] for i in range(5)}
                
                # Rename the columns
                df = df.rename(columns=column_mapping)
        
        # Convert column types
        if 'keyakinan_model' in df.columns:
            df['keyakinan_model'] = pd.to_numeric(df['keyakinan_model'], errors='coerce')
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error getting data from Google Sheets: {e}")
        return pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])

# Initialize Google Sheet
sheet = setup_google_sheets()

# Halaman Utama
st.title("♻️ RecycleLens")
st.markdown("Suggests a clear view into recyclability")

# Tab Navigasi - Add new History & Map tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Deteksi Sampah", "📦 Kategori Sampah", "📷 Panduan", "🧠 Tentang Kami", "🗺️ Riwayat & Peta"])

# JavaScript for browser geolocation
def get_geolocation():
    # Create a unique key for the component session state
    location_key = "browser_location"
    
    # Initialize session state for location if not exists
    if location_key not in st.session_state:
        st.session_state[location_key] = {"lat": None, "lon": None}
    
    # HTML component for automatic geolocation - removed the 'key' parameter
    components.html(
        """
        <script>
        const sendDataToStreamlit = () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        
                        // Store values in sessionStorage
                        sessionStorage.setItem('browser_lat', lat);
                        sessionStorage.setItem('browser_lon', lon);
                        
                        // Display values with better styling
                        document.getElementById('location_status').innerHTML = 
                            '<div style="padding: 8px; border-radius: 4px; background-color: #f0f2f6; margin: 8px 0;">' +
                            '<b>📍 Koordinat kamu ada di:</b> ' + lat + ', ' + lon +
                            '</div>';
                    },
                    (error) => {
                        console.error("Error getting location:", error);
                        document.getElementById('location_status').innerHTML = 
                            '<div style="padding: 8px; border-radius: 4px; background-color: #f8d7da; margin: 8px 0;">' +
                            'Error: Could not get location' +
                            '</div>';
                    }
                );
            } else {
                console.error("Geolocation is not supported by this browser.");
                document.getElementById('location_status').innerHTML = 
                    '<div style="padding: 8px; border-radius: 4px; background-color: #f8d7da; margin: 8px 0;">' +
                    'Error: Geolocation not supported' +
                    '</div>';
            }
        };
        sendDataToStreamlit();
        </script>
        <p id="location_status">Requesting location...</p>
        """,
        height=60
        # Removed 'key' parameter that was causing the error
    )
    
    # Add manual input fields for coordinates
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=0.0, format="%.8f", key="lat_input")
    with col2:
        lon = st.number_input("Longitude", value=0.0, format="%.8f", key="lon_input")
    
    # Store values in session state
    st.session_state[location_key]["lat"] = lat
    st.session_state[location_key]["lon"] = lon
    
    # Return the coordinates
    return {"lat": lat, "lon": lon}

# Tab 1: Deteksi Sampah
with tab1:
    st.subheader("🔍 Unggah atau Ambil Gambar Sampah")

    option = st.radio("Pilih metode input gambar:", ["📁 Upload File", "📷 Kamera"], horizontal=True)

    image = None 
    
    # Geolocation section
    st.subheader("📍 Lokasi")
    
    # Get geolocation directly
    geolocation_data = get_geolocation()
    latitude = geolocation_data["lat"] 
    longitude = geolocation_data["lon"]
    
    # Rest of your code that uses latitude and longitude...
    if option == "📁 Upload File":
        uploaded_file = st.file_uploader("Upload gambar dari perangkat", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)

    elif option == "📷 Kamera":
        camera_image = st.camera_input("Ambil gambar dari kamera")
        if camera_image:
            image = Image.open(camera_image)

    if image:
        label, confidence = predict_image(image)
        info = recycle_guide[label]

        col1, spacer, col2 = st.columns([1, 0.1, 2])
        with col1:
            st.image(image, caption="Gambar yang Diambil", use_container_width=True)
        with col2:
            st.success(f"Prediksi Kategori Sampah: **{label.capitalize()}** ({confidence*100:.2f}%)")
            st.markdown("### ♻️ Cara Daur Ulang")
            st.markdown(info['recycling_info'])
            st.markdown("### 🌍 Dampak Lingkungan")
            st.markdown(info['impact'])
            st.markdown("### 🔥 Jejak Karbon")
            st.markdown(info['carbon_footprint'])
        
        # Save detection with location
        if st.button("Simpan Riwayat Deteksi"):
            if latitude is not None and longitude is not None:
                success = save_detection_to_sheets(label, confidence*100, latitude, longitude)
                if success:
                    st.success("Data deteksi berhasil disimpan ke Google Sheets!")
                else:
                    st.error("Gagal menyimpan data ke Google Sheets.")
            else:
                st.error("Gagal menyimpan data. Lokasi tidak tersedia.")

# Tab 2: Kategori Sampah
with tab2:
    st.subheader("📦 Kategori Sampah & Informasi Daur Ulang")
    for cat in CATEGORIES:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(f"assets/icons/{cat}.png", use_container_width=True)
        with col2:
            info = recycle_guide[cat]
            st.markdown(f"## {cat.capitalize()}")
            st.markdown(f"**Bisa didaur ulang:** {'✅' if info['can_recycle'] else '❌'}")

            with st.expander("♻️ Cara Daur Ulang"):
                st.markdown(info['recycling_info'])

            with st.expander("🌍 Dampak Lingkungan"):
                st.markdown(info['impact'])

            with st.expander("🔥 Jejak Karbon"):
                st.markdown(info['carbon_footprint'])
        st.divider()

# Tab 3: Panduan Upload
with tab3:
    col1, spacer,col2 = st.columns([1, 0.1, 2])
    with col1:
        st.image("assets/sample_image.png", caption="Contoh Gambar yang Baik", use_container_width=True)
    with col2:
        st.subheader("📷 Panduan Upload Gambar")
        st.markdown("""
        Agar hasil prediksi lebih akurat:
        - Gambar terang dan tidak blur 
        - Fokus hanya pada satu jenis sampah
        - Hindari latar belakang ramai
        - Pastikan benda sampah tidak terpotong
        """)  

# Tab 4: Tentang Kami
with tab4:
    col1, spacer,col2 = st.columns([1, 0.1, 2])
    with col1:
        st.image("assets/sampah.jpg", caption="Ilustrasi tumpukan sampah di Indonesia", use_container_width=True)
    with col2:
        st.image("assets/logo_recyclelens.png", width=400)
        st.write("""
        Indonesia menghadapi tantangan besar dalam pengelolaan sampah. Menurut data [SIPSN 2024](https://sipsn.menlhk.go.id), hanya sekitar 60% dari total 33,6 juta ton sampah yang berhasil dikelola dengan baik setiap tahun. Selebihnya berpotensi mencemari lingkungan dan menyebabkan kerusakan jangka panjang.

        **RecycleLens** dikembangkan sebagai solusi berbasis kecerdasan buatan untuk:
        - Mengklasifikasikan sampah dari gambar
        - Memberikan edukasi dan saran daur ulang
        - Mendorong masyarakat untuk lebih sadar lingkungan

        Proyek ini merupakan bagian dari **Capstone Laskar AI 2025 (LAI25-SM014)** yang beranggotakan:
        - A184YBM526 – Agum Medisa – Universitas Andalas 
        - A873XAF389 – Oryza Khairunnisa – Tokyo Metropolitan University 
        - A012XBF173 – Filza Rahma Muflihah – Universitas Telkom 
        - A010YBM333 – Muhammad Nafriel Ramadhan – Universitas Indonesia 
        """)

# Tab 5: History & Map - dengan fitur filter dan fokus
with tab5:
    st.subheader("🗺️ Riwayat Deteksi & Peta Sebaran Sampah")
    
    # Get history data
    history_data = get_detection_history()
    
    # Debug information about columns
    if not history_data.empty:
        st.sidebar.write("Debug: Actual columns in DataFrame:", history_data.columns.tolist())
    
    # Initialize valid_locations as empty DataFrame to avoid reference errors
    valid_locations = pd.DataFrame(columns=['timestamp', 'jenis_sampah', 'keyakinan_model', 'latitude', 'longitude'])
    
    # Display data table
    if not history_data.empty:
        st.subheader("📊 Tabel Riwayat Deteksi")
        
        # Check if required columns exist and handle case sensitivity issues
        column_map = {}
        for expected_col in ['jenis_sampah', 'timestamp', 'keyakinan_model', 'latitude', 'longitude']:
            # Try to find column with case-insensitive match
            matches = [col for col in history_data.columns if col.lower() == expected_col.lower()]
            if matches:
                column_map[expected_col] = matches[0]
        
        # Rename columns to expected format if needed
        if column_map and len(column_map) > 0:
            history_data = history_data.rename(columns={v: k for k, v in column_map.items()})
        
        # Add filter option at the top - with safety checks
        if 'jenis_sampah' in history_data.columns:
            all_waste_types = history_data['jenis_sampah'].unique().tolist()
            filter_options = ["Semua Jenis"] + [type.capitalize() for type in all_waste_types]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_filter = st.selectbox("Filter berdasarkan jenis sampah:", filter_options)
            
            # Filter the data if needed
            if selected_filter != "Semua Jenis":
                filtered_data = history_data[history_data['jenis_sampah'].str.lower() == selected_filter.lower()]
                st.dataframe(filtered_data, use_container_width=True)
            else:
                filtered_data = history_data
                st.dataframe(filtered_data, use_container_width=True)
            
            # Create map visualization
            st.subheader("🗺️ Peta Sebaran Deteksi Sampah")
            
            # Exclude 0,0 coordinates (invalid data points)
            valid_locations = filtered_data[(filtered_data['latitude'] != 0) | (filtered_data['longitude'] != 0)]
            valid_locations = valid_locations.dropna(subset=['latitude', 'longitude'])
            
            # Add option to focus on a specific detection
            if not valid_locations.empty:
                # Create a selection widget for focusing on specific entries
                with col2:
                    if "focus_index" not in st.session_state:
                        st.session_state["focus_index"] = 0
                    
                    timestamps = ["Otomatis"] + valid_locations['timestamp'].tolist()
                    selected_timestamp = st.selectbox(
                        "Fokus ke lokasi:",
                        timestamps,
                        index=st.session_state["focus_index"]
                    )
                    
                    # Update session state when selection changes
                    focus_index = timestamps.index(selected_timestamp)
                    st.session_state["focus_index"] = focus_index
                
                # Determine map center and zoom based on selection
                if selected_timestamp != "Otomatis" and focus_index > 0:
                    # Focus on selected detection
                    focus_row = valid_locations[valid_locations['timestamp'] == selected_timestamp].iloc[0]
                    center_lat = focus_row['latitude']
                    center_lon = focus_row['longitude']
                    zoom_level = 18  # Closer zoom when focusing on a specific point
                else:
                    # Center map on average coordinates
                    center_lat = valid_locations['latitude'].mean()
                    center_lon = valid_locations['longitude'].mean()
                    zoom_level = 15  # Default zoom for overview
                
                # Create map with proper zoom level
                m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, 
                              tiles="OpenStreetMap")
                
                # Add markers for each detection with custom colors and popups
                colors = {
                    'cardboard': 'orange', 
                    'glass': 'blue', 
                    'metal': 'gray',
                    'paper': 'green', 
                    'plastic': 'red', 
                    'trash': 'black'
                }
                
                # Add markers loop with highlighted focus marker
                for idx, row in valid_locations.iterrows():
                    # Get color based on waste type or default to darkblue
                    color = colors.get(str(row['jenis_sampah']).lower(), 'darkblue')
                    
                    # Format confidence to 2 decimal places
                    confidence = float(row['keyakinan_model'])
                    
                    # Create detailed popup content
                    popup_html = f"""
                    <div style="width:200px">
                        <h4 style="color:{color}">{str(row['jenis_sampah']).capitalize()}</h4>
                        <p><b>Keyakinan:</b> {confidence:.2f}%</p>
                        <p><b>Waktu:</b> {row['timestamp']}</p>
                        <p><b>Koordinat:</b> {row['latitude']:.6f}, {row['longitude']:.6f}</p>
                    </div>
                    """
                    
                    # Check if this is the focused marker
                    is_focused = (selected_timestamp != "Otomatis" and row['timestamp'] == selected_timestamp)
                    
                    # Use a larger, different icon for the focused marker
                    if is_focused:
                        icon = folium.Icon(
                            color=color,
                            icon='star',
                            prefix='fa',
                            icon_color='yellow'
                        )
                        # Add a circle to highlight the focused marker
                        folium.Circle(
                            location=[row['latitude'], row['longitude']],
                            radius=20,  # meters
                            color=color,
                            fill=True,
                            fill_opacity=0.3
                        ).add_to(m)
                    else:
                        icon = folium.Icon(
                            color=color, 
                            icon='trash', 
                            prefix='fa'
                        )
                    
                    # Add marker with tooltip and popup
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{str(row['jenis_sampah']).capitalize()} ({confidence:.1f}%)",
                        icon=icon
                    ).add_to(m)
                
                # Display the map
                folium_static(m, width=800, height=500)
                
                # Display legend with interactive filtering capabilities
                st.subheader("Keterangan Warna & Filter")
                
                # Create legend as clickable buttons
                legend_cols = st.columns(len(colors))
                
                # In the legend section of Tab 5, update the filter buttons code
                for i, (waste_type, color) in enumerate(colors.items()):
                    with legend_cols[i]:
                        # Create a button-like element for each waste type
                        if st.button(
                            waste_type.capitalize(),
                            key=f"filter_{waste_type}",
                            help=f"Klik untuk melihat hanya sampah jenis {waste_type}"
                        ):
                            # Replace st.experimental_set_query_params with direct assignment to st.query_params
                            st.query_params["filter"] = waste_type
                            # Replace st.experimental_rerun() with st.rerun()
                            st.rerun()
                        
                        # Show color indicator
                        st.markdown(f"""
                        <div style="background-color: {color}; width: 100%; height: 5px; margin-bottom: 10px; border-radius: 2px;"></div>
                        """, unsafe_allow_html=True)
                
                # Update the "Show All" button code
                if st.button("Tampilkan Semua", key="show_all"):
                    # Clear filter parameters using the new approach
                    st.query_params.clear()
                    # Replace st.experimental_rerun() with st.rerun()
                    st.rerun()
            else:
                st.warning("Belum ada data lokasi valid untuk ditampilkan pada peta. Koordinat tidak boleh (0,0) dan harus terisi.")
        else:
            st.info("Belum ada data deteksi sampah. Silahkan lakukan deteksi pada tab 'Deteksi Sampah' terlebih dahulu.")
        
        # Add new analytics section
        if not valid_locations.empty:
            # New Analytics Section
            st.header("📊 Analisis Data Sampah")
            
            # 1. ANALISIS DISTRIBUSI JENIS SAMPAH
            st.subheader("Analisis Distribusi Jenis Sampah")
            st.write("""
            Analisis ini menunjukkan perbandingan jumlah dan persentase masing-masing jenis sampah
            yang telah terdeteksi, sehingga dapat diketahui jenis sampah apa yang paling dominan.
            """)
            
            # Count frequency of each waste type
            waste_counts = history_data['jenis_sampah'].value_counts().reset_index()
            waste_counts.columns = ['Jenis Sampah', 'Jumlah']
            
            # Calculate percentages
            total = waste_counts['Jumlah'].sum()
            waste_counts['Persentase'] = (waste_counts['Jumlah'] / total * 100).round(2)
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create bar chart with plotly
                fig = px.bar(
                    waste_counts, 
                    x='Jenis Sampah', 
                    y='Jumlah',
                    text='Persentase',
                    color='Jenis Sampah',
                    labels={'Jumlah': 'Frekuensi', 'Jenis Sampah': 'Kategori Sampah'},
                    title='Distribusi Jenis Sampah',
                    template='plotly_white',
                    color_discrete_map={
                        'cardboard': 'orange',
                        'glass': 'blue',
                        'metal': 'gray',
                        'paper': 'green',
                        'plastic': 'red',
                        'trash': 'black'
                    }
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Show data table
                st.write("#### Data Distribusi:")
                st.dataframe(waste_counts, use_container_width=True)
                
                # Show insights
                most_common = waste_counts.iloc[0]['Jenis Sampah']
                most_common_pct = waste_counts.iloc[0]['Persentase']
                st.info(f"📌 **Insight:** Sampah jenis **{most_common}** adalah yang paling sering ditemukan, mewakili **{most_common_pct:.1f}%** dari semua deteksi.")
            
            # 2. ANALISIS SPASIAL (POLA LOKASI SAMPAH)
            st.subheader("Analisis Spasial (Pola Lokasi Sampah)")
            st.write("""
            Analisis ini menunjukkan distribusi geografis dari berbagai jenis sampah,
            membantu mengidentifikasi area atau "hotspot" dengan konsentrasi jenis sampah tertentu.
            """)
            
            # Group by location grid (round to 4 decimal places for grouping nearby points)
            valid_locations['lat_grid'] = np.round(valid_locations['latitude'], 4)
            valid_locations['lon_grid'] = np.round(valid_locations['longitude'], 4)
            
            # Count waste types in each grid cell
            grid_counts = valid_locations.groupby(['lat_grid', 'lon_grid', 'jenis_sampah']).size().reset_index(name='count')
            
            if len(grid_counts) > 0:
                # Find dominant waste type in each grid cell
                try:
                    dominant_waste = grid_counts.loc[grid_counts.groupby(['lat_grid', 'lon_grid'])['count'].idxmax()]
                
                    # Create a map showing the dominant waste type in each area
                    st.write("#### Peta Hotspot Sampah")
                    st.write("Peta ini menunjukkan area dengan konsentrasi jenis sampah tertentu. Lingkaran lebih besar menunjukkan jumlah yang lebih tinggi.")
                    
                    hotspot_map = folium.Map(location=[center_lat, center_lon], zoom_start=15,
                                           tiles="CartoDB positron")
                    
                    # Add markers for hotspots
                    for idx, row in dominant_waste.iterrows():
                        # Get color for this waste type
                        color = colors.get(str(row['jenis_sampah']).lower(), 'darkblue')
                        
                        # Add circle marker sized by count
                        folium.CircleMarker(
                            location=[row['lat_grid'], row['lon_grid']],
                            radius=5 + (row['count'] * 2),  # Base size + adjustment for count
                            popup=f"""
                            <div style="width:200px">
                                <h4>Hotspot Sampah</h4>
                                <p><b>Jenis dominan:</b> {row['jenis_sampah'].capitalize()}</p>
                                <p><b>Jumlah:</b> {row['count']} item</p>
                                <p><b>Lokasi:</b> {row['lat_grid']:.6f}, {row['lon_grid']:.6f}</p>
                            </div>
                            """,
                            tooltip=f"{row['jenis_sampah'].capitalize()}: {row['count']} item",
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.6,
                            weight=2
                        ).add_to(hotspot_map)
                    
                    # Add layer control and other map elements
                    folium.LayerControl().add_to(hotspot_map)
                    
                    # Display the hotspot map
                    folium_static(hotspot_map, width=800, height=500)
                    
                    # Display results in a table
                    st.write("#### Tabel Hotspot Jenis Sampah")
                    hotspot_table = dominant_waste.copy()
                    hotspot_table.columns = ['Latitude', 'Longitude', 'Jenis Sampah Dominan', 'Jumlah']
                    st.dataframe(hotspot_table, use_container_width=True)
                    
                    # Generate insights from the data
                    if len(hotspot_table) > 1:
                        # Find the location with highest concentration
                        max_loc = hotspot_table.loc[hotspot_table['Jumlah'].idxmax()]
                        st.info(f"""
                        📌 **Insight:** Konsentrasi sampah tertinggi ditemukan di sekitar koordinat 
                        **{max_loc['Latitude']:.6f}, {max_loc['Longitude']:.6f}** dengan **{max_loc['Jumlah']}** item 
                        sampah jenis **{max_loc['Jenis Sampah Dominan']}**.
                        """)
                    
                    # Check if there are different waste types in different areas
                    waste_variety = hotspot_table['Jenis Sampah Dominan'].nunique()
                    if waste_variety > 1:
                        st.success(f"""
                        🔍 **Pola Spasial Terdeteksi:** Terdeteksi **{waste_variety}** jenis sampah dominan
                        di area yang berbeda. Hal ini menunjukkan adanya pola distribusi spasial yang spesifik
                        untuk jenis sampah tertentu.
                        """)
                except Exception as e:
                    st.warning(f"Tidak dapat menghitung hotspot: {e}")
            else:
                st.warning("Belum cukup data untuk analisis hotspot. Diperlukan lebih banyak titik data.")



