import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import numpy as np
import av

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="FocusGuard AI", page_icon="🧠", layout="centered")

# Custom CSS to make the UI look like a premium product
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5em; background-color: #2e7d32; color: white; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def change_page(page_name):
    st.session_state.page = page_name

# --- 3. PAGE: HOME / INSTRUCTIONS ---
if st.session_state.page == 'Home':
    st.title("🚀 FocusGuard AI")
    st.subheader("Master your productivity with Real-Time AI Monitoring.")
    
    st.info("💡 **Instructions for Students:**")
    st.markdown("""
    * **Environment:** Sit in a well-lit area.
    * **Setup:** Position your camera so your face is centered.
    * **Monitoring:** The AI tracks your presence. Looking away or leaving will lower your score.
    * **Privacy:** Processing happens locally in your browser. No data is stored.
    """)
    
    st.button("Launch Live Session", on_click=change_page, args=('App',))
    
    st.write("---")
    st.caption("Ad Space")
    st.image("https://via.placeholder.com/728x90.png?text=Google+AdSense+Horizontal+Banner", use_container_width=True)

# --- 4. PAGE: LIVE MONITORING ---
elif st.session_state.page == 'App':
    st.title("🧠 Live Focus Monitor")
    st.button("⬅ Back to Home", on_click=change_page, args=('Home',))

    # The AI Processing Engine
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
                    # Professional green tracking box
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.putText(img, "FOCUSING", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")

    # --- 5. THE LIVE WEB-STREAM ---
    ctx = webrtc_streamer(
        key="focus-stream",
        video_processor_factory=FocusProcessor,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        media_stream_constraints={"video": True, "audio": False},
    )

    # --- 6. STATS & REVENUE ---
    if ctx.video_processor:
        st.write("---")
        col1, col2 = st.columns(2)
        
        total = ctx.video_processor.total_frames
        count = ctx.video_processor.focus_count
        rate = (count / total * 100) if total > 0 else 0
        
        with col1:
            st.metric("Live Focus Rate", f"{rate:.2f}%")
        with col2:
            status = "✅ ACTIVE" if rate > 60 else "⚠️ DISTRACTED"
            st.metric("Session Status", status)

    # Sidebar Revenue/Ad Sections
    st.sidebar.title("App Sponsors")
    st.sidebar.markdown("Help keep FocusGuard free for everyone!")
    st.sidebar.image("https://via.placeholder.com/300x250.png?text=Sidebar+Ad+Banner")
    st.sidebar.write("---")
    if st.sidebar.button("End & Clear Session"):
        st.session_state.clear()
        st.rerun()
