import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import numpy as np
import av

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="FocusGuard AI", page_icon="🧠", layout="centered")

# --- 2. NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def change_page(p): 
    st.session_state.page = p

# --- 3. PAGE: HOME / INSTRUCTIONS ---
if st.session_state.page == 'Home':
    st.title("🚀 FocusGuard AI")
    st.subheader("Master your productivity with Real-Time AI Monitoring.")
    
    st.markdown("""
    ### 📝 Quick Start Guide:
    1. **Position yourself** in a well-lit area.
    2. **Launch the Monitor** to start tracking.
    3. **Stay Focused:** The AI alerts you if you look away.
    """)
    
    if st.button("Launch Live Session"):
        change_page('App')
        st.rerun()

    st.write("---")
    st.caption("Ad Space")
    st.image("https://via.placeholder.com/728x90.png?text=Google+AdSense+Banner")

# --- 4. PAGE: LIVE MONITORING ---
elif st.session_state.page == 'App':
    st.title("🧠 Live Focus Monitor")
    if st.button("⬅ Back to Home"):
        change_page('Home')
        st.rerun()

    class FocusProcessor(VideoProcessorBase):
        def __init__(self):
            # Load the face detection model
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.focus_count = 0
            self.total_frames = 0

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            self.total_frames += 1
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                self.focus_count += 1
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")

    # THE LIVE STREAM
    ctx = webrtc_streamer(
        key="focus-stream",
        video_processor_factory=FocusProcessor,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        media_stream_constraints={"video": True, "audio": False},
    )

    if ctx.video_processor:
        t = ctx.video_processor.total_frames
        c = ctx.video_processor.focus_count
        rate = (c / t * 100) if t > 0 else 0
        st.metric("Live Focus Rate", f"{rate:.2f}%")

    # SIDEBAR REVENUE
    st.sidebar.title("App Sponsors")
    st.sidebar.image("https://via.placeholder.com/300x250.png?text=Sidebar+Ad")
