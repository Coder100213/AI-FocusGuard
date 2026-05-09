import streamlit as st
import cv2
import numpy as np

# --- PAGE UI SETUP ---
st.set_page_config(page_title="FocusGuard AI", page_icon="🎓", layout="wide")

# Custom CSS for a professional Student Dashboard look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
        color: #e8f5e9;
    }
    .report-card {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session variables
if "step" not in st.session_state:
    st.session_state.step = "setup"
    st.session_state.total_frames = 0
    st.session_state.study_frames = 0

# --- STEP 1: WELCOME PAGE ---
if st.session_state.step == "setup":
    st.title("🎓 FocusGuard AI")
    st.markdown("#### *Your Intelligent Study Companion*")

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.markdown("""
        ### Ready to level up your focus? 🚀
        This app uses **Computer Vision** to track your study habits. 
        It rewards you for engaging with your books and stays active even when you are reading deeply.

        **Instructions:**
        1. Place your **book or notebook** clearly on the desk.
        2. Ensure you are sitting in the center of the camera.
        3. Click the button below to begin your session!
        """)

        # Hyperlink to the technical section
        st.markdown("🔗 [**How does this AI actually work? (Technical Explanation)**](#how-it-works)")

        if st.button("🚀 START MY SESSION"):
            st.session_state.total_frames = 0
            st.session_state.study_frames = 0
            st.session_state.step = "monitoring"
            st.rerun()

    with col2:
        # FIXED: Removed the 'Sale' banner from Screenshot 2026-05-09 at 18.59.12.jpg
        # and replaced with a stable study icon. Fixed the deprecation warning.
        st.image("https://cdn-icons-png.flaticon.com/512/3407/3407154.png", width=320)

    st.divider()

    # Technical explanation section with anchor for the hyperlink
    st.markdown("<div id='how-it-works'></div>", unsafe_allow_html=True)
    with st.expander("🧠 The Science Behind FocusGuard AI"):
        st.write("""
        This app uses a multi-layered **Artificial Intelligence pipeline**:
        1.  **Face Analysis:** Uses *Haar Cascades* to detect your presence.
        2.  **Geometric Detection:** Uses *Canny Edge Detection* to find the rectangular borders of your book.
        3.  **Heuristic Logic:** Unlike basic AI, this system recognizes 'Deep Study' mode—if you look down at the book and your face 'disappears' from the camera, the AI knows you are still working!
        """)

# --- STEP 2: MONITORING MODE ---
elif st.session_state.step == "monitoring":
    st.title("✍️ Session in Progress...")

    col_vid, col_stats = st.columns([2, 1])

    with col_vid:
        FRAME_WINDOW = st.image([])
        stop_btn = st.button("🛑 FINISH & SEE SCORE")

    with col_stats:
        st.markdown("### 📊 Live Analytics")
        status_box = st.empty()
        score_metric = st.empty()
        warning_area = st.empty()
        st.info("💡 **Pro-Tip:** Make sure the camera can see the edges of your book!")

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while not stop_btn:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        st.session_state.total_frames += 1

        # Image Processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        faces = face_cascade.detectMultiScale(blur, 1.3, 5)

        # Robust Book Detection
        edged = cv2.Canny(blur, 50, 150)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        book_found = any(cv2.contourArea(c) > (h * w * 0.10) for c in contours)

        # Logical Decision Engine
        if book_found:
            warning_area.empty()
            st.session_state.study_frames += 1
            if len(faces) > 0:
                status = "✅ ACTIVE STUDYING"
                color = (0, 255, 0)
            else:
                status = "📖 DEEP READING"
                color = (0, 255, 255)
        else:
            status = "❌ NO BOOK DETECTED"
            color = (0, 0, 255)
            warning_area.error("⚠️ Please place your book in the frame!")

        # Update Video Feed
        cv2.putText(frame, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        FRAME_WINDOW.image(frame, channels="BGR")

        # Update Dashboard Stats
        current_score = (st.session_state.study_frames / st.session_state.total_frames) * 100
        status_box.markdown(f"**Current State:** {status}")
        score_metric.metric("Integrity Score", f"{current_score:.1f}%")

        if stop_btn: break

    cap.release()
    st.session_state.step = "report"
    st.rerun()

# --- STEP 3: FINAL REPORT ---
elif st.session_state.step == "report":
    st.balloons()
    st.title("🏆 Study Session Complete")

    total = st.session_state.total_frames
    study = st.session_state.study_frames
    final_score = (study / total * 100) if total > 0 else 0

    st.markdown(f"""
    <div class="report-card">
        <h1>Grade: {final_score:.1f}%</h1>
        <p style="font-size: 1.2em; color: #666;">
            {"Excellent focus! You're mastering the material." if final_score > 80 else "Good effort, but try to keep your book in view more often!"}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")  # Spacer
    if st.button("🔄 START NEW SESSION"):
        st.session_state.step = "setup"
        st.rerun()