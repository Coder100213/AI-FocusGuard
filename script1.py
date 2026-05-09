import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="FocusGuard AI", layout="centered")

# Custom CSS to make it look professional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (YOUR AD SPACE) ---
with st.sidebar:
    st.title("📊 Session Stats")
    if 'start_time' in st.session_state:
        elapsed = int(time.time() - st.session_state.start_time)
        st.metric("Focus Time", f"{elapsed // 60}m {elapsed % 60}s")
    
    st.write("---")
    st.write("✨ **Sponsored Content**")
    # This is where you paste your Google AdSense code or a custom banner
    st.info("Your Ad Here: Contact ads@focusguard.com")
    st.write("---")
    st.button("Reset Session", on_click=lambda: st.session_state.clear())

# --- 3. MAIN APP HEADER ---
st.title("🧠 FocusGuard AI")
st.write("Improve your productivity with AI-powered focus tracking.")

# --- 4. THE CORE LOGIC ---
if 'focus_data' not in st.session_state:
    st.session_state.focus_data = []

# Web-friendly camera input
img_file_buffer = st.camera_input("Check your focus posture")

if img_file_buffer is not None:
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

    # Convert image for OpenCV
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # AI Detection Logic (Haar Cascades)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Process Results
    if len(faces) > 0:
        st.session_state.focus_data.append(1)
        st.success("✅ Focus Detected!")
    else:
        st.session_state.focus_data.append(0)
        st.warning("⚠️ No face detected. Are you still there?")

    # Calculate Focus Rate
    focus_rate = (sum(st.session_state.focus_data) / len(st.session_state.focus_data)) * 100
    st.metric("Current Focus Rate", f"{focus_rate:.2f}%")

    # Display Analysis
    for (x, y, w, h) in faces:
        cv2.rectangle(cv2_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
    st.image(cv2_img, channels="BGR", caption="AI Vision Feed")

else:
    st.info("Waiting for camera input to start session...")

# --- 5. FOOTER ADS ---
st.write("---")
# Placeholder for bottom banner ad
st.markdown("<div style='text-align: center; color: gray;'>Advertisement</div>", unsafe_allow_html=True)
st.image("https://via.placeholder.com/728x90.png?text=Your+Banner+Ad+Here", use_container_width=True)
