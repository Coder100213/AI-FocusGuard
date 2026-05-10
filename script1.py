import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import numpy as np

# --- 1. SETTINGS & STYLE ---
st.set_page_config(page_title="FocusGuard AI", page_icon="🧠", layout="centered")

# --- 2. MULTI-PAGE NAVIGATION (Our original flow) ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def go_to_app(): st.session_state.page = 'App'
def go_to_home(): st.session_state.page = 'Home'

# --- 3. PAGE: HOME / INSTRUCTIONS ---
if st.session_state.page == 'Home':
    st.title("🚀 Welcome to FocusGuard AI")
    st.markdown("""
    ### How it Works:
    1. **Position yourself** so your face is clearly visible.
    2. **Start the Monitor** to begin your deep-work session.
    3. **AI Tracking:** Our system monitors your presence and posture.
    4. **Earn Results:** Get a focus report at the end of your session.
    
    *Privacy Note: Everything stays in your browser. We don't store your video.*
    """)
    st.button("Start My Session", on_click=go_to_app)
    
    st.write("---")
    st.caption("v2.0 - Revenue Enabled Build")

# --- 4. PAGE: THE LIVE MONITORING APP ---
elif st.session_state.page == 'App':
    st.title("🧠 Live Focus Monitor")
    st.button("⬅ Back to Home", on_click=go_to_home)

    # The "Brain" of the Live Monitor
    class FocusTransformer(VideoTransformerBase):
        def __init__(self):
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.focus_count = 0
            self.total_frames = 0

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            self.total_frames += 1
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                self.focus_count += 1
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            return img

    # THE LIVE STREAM (This replaces cv2.VideoCapture)
    ctx = webrtc_streamer(
        key="focus-stream", 
        video_transformer_factory=FocusTransformer,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    # --- 5. REAL-TIME REPORTING ---
    if ctx.video_transformer:
        col1, col2 = st.columns(2)
        with col1:
            total = ctx.video_transformer.total_frames
            count = ctx.video_transformer.focus_count
            rate = (count / total * 100) if total > 0 else 0
            st.metric("Live Focus Score", f"{rate:.2f}%")
        with col2:
            st.metric("Session Status", "Active" if rate > 50 else "Distracted")
    
    # --- 6. REVENUE AD SPACE ---
    st.write("---")
    st.sidebar.markdown("### 📢 Sponsors")
    # Paste your AdSense code below in the future
    st.sidebar.info("Support FocusGuard by viewing our partner content.")
    st.sidebar.image("https://via.placeholder.com/300x250.png?text=Ad+Banner+Space")
