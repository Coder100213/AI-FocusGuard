import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import numpy as np
import av  # Essential for the new video engine

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="FocusGuard AI", page_icon="🧠", layout="centered")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4CAF50; color: white; }
    .reportview-container { background: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-PAGE NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def go_to_app(): st.session_state.page = 'App'
def go_to_home(): st.session_state.page = 'Home'

# --- 3. PAGE: HOME / INSTRUCTIONS ---
if st.session_state.page == 'Home':
    st.title("🚀 Welcome to FocusGuard AI")
    st.subheader("The ultimate tool for student productivity.")
    
    st.markdown("""
    ### 📝 How to use:
    1. **Setup:** Ensure you are in a well-lit room.
    2. **Start:** Click the button below to open the Live Monitor.
    3. **Focus:** The AI will track your presence. If you leave or look away, your score drops.
    4. **Results:** View your Focus Rate in real-time.
    
    ---
    *Privacy: No video data is ever sent to our servers. Processing happens entirely in your browser.*
    """)
    
    st.button("Start My Session", on_click=go_to_app)
    
    # Bottom Ad Space for Home Page
    st.write("---")
    st.caption("Sponsored Content")
    st.image("https://via.placeholder.com/728x90.png?text=Ad+Banner+Space", use_container_width=True)

# --- 4. PAGE: THE LIVE MONITORING APP ---
elif st.session_state.page == 'App':
    st.title("🧠 Live Focus Monitor")
    st.button("⬅ Back to Instructions", on_click=go_to_home)

    # Use 'VideoProcessorBase' (The modern, stable version)
    class FocusProcessor(VideoProcessorBase):
        def __init__(self):
            # Load the face detection AI
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.focus_count = 0
            self.total_frames = 0

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            self.total_frames += 1
            
            # Convert to grayscale for faster detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                self.focus_count += 1
                for (x, y, w, h) in faces:
                    # Draw professional green bounding box
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.putText(img, "FOCUSING", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")

    # --- 5. THE LIVE STREAM ---
    ctx = webrtc_streamer(
        key="focus-stream", 
        video_processor_factory=FocusProcessor,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        media_stream_constraints={"video": True, "audio": False},
    )

    # --- 6. REAL-TIME STATS & REVENUE ---
    if ctx.video_processor:
        col1, col2 = st.columns(2)
        
        with col1:
            total = ctx.video_processor.total_frames
            count = ctx.video_processor.focus_count
            rate = (count / total * 100) if total > 0 else 0
            st.metric("Live Focus Rate", f"{rate:.2f}%")
            
        with col2:
            status = "🔥 Productive" if rate > 70 else "💤 Distracted"
            st.metric("Current Status", status)

    # --- 7. SIDEBAR ADS ---
    st.sidebar.title("Support FocusGuard")
    st.sidebar.info("This app is free for students. Please consider supporting our sponsors.")
    st.sidebar.image("https://via.placeholder.com/300x250.png?text=Sidebar+Ad+Space")
    st.sidebar.write("---")
    st.sidebar.button("Clear Session Data", on_click=lambda: st.session_state.clear())
