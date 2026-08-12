import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import tempfile
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EcoBin AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = None

if "image_result" not in st.session_state:
    st.session_state.image_result = None

if "camera_result" not in st.session_state:
    st.session_state.camera_result = None

if "video_result" not in st.session_state:
    st.session_state.video_result = None


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #f4f6fa;
}

.block-container {
    max-width: 1400px;
    padding-top: 25px;
    padding-bottom: 30px;
    padding-left: 7%;
    padding-right: 7%;
}

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.main-title,
.detect-title {
    color: #17345f !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    text-align: center;
}

.main-title {
    margin-bottom: 32px;
}

.detect-title {
    margin-bottom: 5px;
}

.detect-subtitle {
    color: #64748b !important;
    text-align: center;
    font-size: 15px;
    margin-bottom: 25px;
}

.aicw-text {
    color: #17345f !important;
    font-size: 25px !important;
    font-weight: 800 !important;
    line-height: 1.55;
}

.capstone-text {
    color: #334155 !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    margin-top: 42px;
}

.description-title {
    color: #17345f !important;
    font-size: 24px !important;
    font-weight: 800 !important;
    margin-bottom: 12px;
}

.description-box {
    background: #ffffff;
    border: 1px solid #dfe4ec;
    border-radius: 14px;
    padding: 22px;
    color: #374151 !important;
    font-size: 15px;
    line-height: 1.7;
}

.stMarkdown,
.stMarkdown p,
.stMarkdown li {
    color: #374151;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #dfe4ec !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 10px rgba(30, 41, 59, 0.06);
    padding: 8px !important;
}

.card-heading {
    color: #26364d !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    margin-bottom: 16px;
}

.card-text {
    color: #4b5563 !important;
    font-size: 14px !important;
    line-height: 2.2 !important;
}

div.stButton > button {
    width: 100%;
    height: 45px;
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #d5dce6 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

div.stButton > button:hover {
    border-color: #17345f !important;
    color: #17345f !important;
    background: #f8fafc !important;
}

label {
    color: #334155 !important;
}

.detection-box-title {
    color: #17345f !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    margin-bottom: 12px;
}

.alert-box {
    background: #fff1f2;
    border: 2px solid #ef4444;
    border-radius: 12px;
    padding: 18px;
    margin-top: 10px;
    color: #991b1b !important;
}

.normal-box {
    background: #f0fdf4;
    border: 2px solid #22c55e;
    border-radius: 12px;
    padding: 18px;
    margin-top: 10px;
    color: #166534 !important;
}

.footer-text {
    text-align: center;
    color: #64748b;
    margin-top: 35px;
    font-size: 13px;
}

@media(max-width: 900px) {

    .block-container {
        padding-left: 5%;
        padding-right: 5%;
    }

    .main-title,
    .detect-title {
        font-size: 24px !important;
    }

    .aicw-text {
        font-size: 21px !important;
    }

    .capstone-text {
        font-size: 19px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD YOLO MODEL
# ============================================================

@st.cache_resource
def load_model():

    model_path = os.path.join(
        os.path.dirname(__file__),
        "best.pt"
    )

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            "best.pt file not found in the same folder as app.py"
        )

    return YOLO(model_path)


# ============================================================
# LOCATION
# ============================================================

def get_location():

    try:
        location = st.secrets["LOCATION"]

        if location:
            return str(location)

    except Exception:
        pass

    return "Location not configured"


# ============================================================
# CURRENT DATE & TIME
# ============================================================

def get_current_time():

    india_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return india_time.strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )


# ============================================================
# SEND EMAIL
# ============================================================

def send_email_alert():

    try:

        sender_email = st.secrets["EMAIL_SENDER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        receiver_email = st.secrets["EMAIL_RECEIVER"]

        message = EmailMessage()

        message["Subject"] = (
            "EcoBin AI - Garbage Overflow Alert"
        )

        message["From"] = sender_email
        message["To"] = receiver_email

        message.set_content(
            f"""
GARBAGE OVERFLOW DETECTED!

EcoBin AI - Smart Garbage Overflow Detection System

Location:
{get_location()}

Date & Time:
{get_current_time()}

Status:
Violation Detected

Detection Class:
overclass

This alert was automatically generated by EcoBin AI.
"""
        )

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.send_message(message)

        return True

    except Exception as e:

        st.error(
            f"Email alert failed: {e}"
        )

        return False


# ============================================================
# GENERATE ALERT
# ============================================================

def generate_alert():

    current_dt = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    previous = st.session_state.last_alert_time

    if previous is not None:

        difference = (
            current_dt - previous
        ).total_seconds()

        if difference < 300:
            return

    st.session_state.last_alert_time = current_dt

    email_sent = send_email_alert()

    if email_sent:
        st.success(
            "📧 Alert email sent successfully."
        )


# ============================================================
# CLASS NAME NORMALIZATION
# ============================================================

def normalize_class_name(name):

    name = str(name).lower().strip()

    name = name.replace("_", " ")
    name = name.replace("-", " ")

    return name


# ============================================================
# GET DETECTIONS FROM YOLO RESULT
# ============================================================

def extract_detections(result):

    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = normalize_class_name(
            result.names[class_id]
        )

        detections.append({
            "class": class_name,
            "confidence": confidence
        })

    return detections


# ============================================================
# FINAL PREDICTION
# ============================================================

def get_final_prediction(detections):

    """
    Final decision:

    1. overclass with confidence >= 0.30
       => GARBAGE OVERFLOW

    2. otherwise normal detection
       => NORMAL

    3. otherwise
       => NO CLEAR DETECTION
    """

    over_detections = [
        d for d in detections
        if d["class"] in [
            "overclass",
            "overflow",
            "garbage overflow",
            "overflowing",
            "overflowed"
        ]
        and d["confidence"] >= 0.30
    ]

    normal_detections = [
        d for d in detections
        if d["class"] in [
            "normal",
            "normal bin",
            "non overflow",
            "non-overflow"
        ]
    ]

    if over_detections:

        best = max(
            over_detections,
            key=lambda x: x["confidence"]
        )

        return (
            "GARBAGE OVERFLOW",
            best["confidence"]
        )

    if normal_detections:

        best = max(
            normal_detections,
            key=lambda x: x["confidence"]
        )

        return (
            "NORMAL",
            best["confidence"]
        )

    return (
        "NO CLEAR DETECTION",
        0.0
    )


# ============================================================
# PREDICT IMAGE
# ============================================================

def predict_image(image, model):

    image_np = np.array(image)

    results = model.predict(
        source=image_np,
        conf=0.20,
        verbose=False
    )

    result = results[0]

    detections = extract_detections(result)

    return result, detections


# ============================================================
# DISPLAY PREDICTION
# ============================================================

def display_prediction(
    result,
    detections,
    title="Prediction Result"
):

    st.markdown(
        f'<div class="detection-box-title">{title}</div>',
        unsafe_allow_html=True
    )

    annotated = result.plot()

    st.image(
        annotated,
        use_container_width=True
    )

    status, confidence = get_final_prediction(
        detections
    )

    st.write("")

    if status == "GARBAGE OVERFLOW":

        st.markdown(
            f"""
            <div class="alert-box">

            <h3>🚨 Garbage Overflow Detected</h3>

            <b>Detection:</b> overclass<br><br>

            <b>Confidence:</b>
            {confidence * 100:.2f}%<br><br>

            <b>📍 Location:</b>
            {get_location()}<br><br>

            <b>🕒 Date & Time:</b>
            {get_current_time()}<br><br>

            <b>⚠️ Status:</b>
            Violation Detected

            </div>
            """,
            unsafe_allow_html=True
        )

        generate_alert()

    elif status == "NORMAL":

        st.markdown(
            f"""
            <div class="normal-box">

            <h3>✅ No Garbage Overflow Detected</h3>

            <b>Detection:</b> normal<br><br>

            <b>Confidence:</b>
            {confidence * 100:.2f}%<br><br>

            <b>Status:</b>
            Normal

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "⚠️ No clear garbage condition detected. "
            "Please try another image/video."
        )

    if detections:

        st.write("")

        st.markdown(
            "**Detection Details**"
        )

        for detection in detections:

            st.write(
                f"• {detection['class']} — "
                f"{detection['confidence'] * 100:.2f}%"
            )


# ============================================================
# PROCESS VIDEO
# ============================================================

def process_video(video_path, model):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return "NO CLEAR DETECTION", None, 0.0

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    frame_skip = max(
        int(fps),
        1
    )

    frame_number = 0

    overflow_count = 0
    normal_count = 0
    detection_count = 0

    best_frame = None
    best_overflow_confidence = 0.0

    progress = st.progress(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_number % frame_skip == 0:

            results = model.predict(
                source=frame,
                conf=0.20,
                verbose=False
            )

            result = results[0]

            detections = extract_detections(
                result
            )

            status, confidence = get_final_prediction(
                detections
            )

            if status == "GARBAGE OVERFLOW":

                overflow_count += 1
                detection_count += 1

                if confidence > best_overflow_confidence:

                    best_overflow_confidence = confidence

                    best_frame = result.plot()

            elif status == "NORMAL":

                normal_count += 1
                detection_count += 1

        frame_number += 1

        if total_frames > 0:

            progress.progress(
                min(
                    frame_number / total_frames,
                    1.0
                )
            )

    cap.release()

    progress.empty()

    if detection_count == 0:

        return (
            "NO CLEAR DETECTION",
            None,
            0.0
        )

    # If overflow appears in any sampled frame,
    # treat the CCTV event as overflow.
    if overflow_count > 0:

        return (
            "GARBAGE OVERFLOW",
            best_frame,
            best_overflow_confidence
        )

    return (
        "NORMAL",
        None,
        0.0
    )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.markdown(
        '<div class="main-title">'
        '♻️ EcoBin AI – Smart Garbage Overflow Detection'
        '</div>',
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns(
        [0.38, 0.62],
        gap="large"
    )

    with left_col:

        st.markdown(
            '<div class="aicw-text">'
            'AI Career for Women'
            '<br>'
            '(AICW)'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="capstone-text">'
            'Capstone Project'
            '</div>',
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "🔍  PREDICT",
            key="predict",
            use_container_width=True
        ):

            st.session_state.page = "predict"
            st.rerun()

    with right_col:

        st.markdown(
            '<div class="description-title">'
            'Project Description'
            '</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):

            st.markdown(
                """
                EcoBin AI is an AI-powered Smart Garbage Overflow
                Detection System designed to automatically identify
                overflowing garbage bins using computer vision and
                YOLOv8 object detection.

                The system analyzes images, camera-captured photos,
                and CCTV/video files to identify garbage overflow
                conditions. The trained YOLOv8 model classifies the
                detected garbage condition into two classes:
                <b>overclass</b> and <b>normal</b>.

                When an overflow condition is detected, EcoBin AI
                automatically generates an alert containing the
                location, date and time, and violation status.
                The alert is also sent to the configured user's
                email address.

                This system helps reduce manual monitoring effort,
                support faster waste-management response, and
                improve cleanliness in public and residential areas.
                """,
                unsafe_allow_html=True
            )

    st.write("")
    st.write("")

    team_col, gmail_col, guide_col = st.columns(
        [1.25, 1.25, 0.75],
        gap="large"
    )

    with team_col:

        with st.container(border=True):

            st.markdown(
                '<div class="card-heading">'
                'TEAM MEMBERS'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="card-text">

                1. K.Lalitha Devi<br>
                2. Y.Haasini<br>
                3. G.Sri Divya<br>
                4. N.Sushma sri

                </div>
                """,
                unsafe_allow_html=True
            )

    with gmail_col:

        with st.container(border=True):

            st.markdown(
                '<div class="card-heading">'
                'GMAIL'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="card-text">

                lalithadevi825@gmail.com<br>
                haasiniyanamadala@gmail.com<br>
                galidivya534@gmail.com<br>
                nadimpallisushmasri29@gmail.com

                </div>
                """,
                unsafe_allow_html=True
            )

    with guide_col:

        with st.container(border=True):

            st.markdown(
                '<div class="card-heading">'
                'GUIDE NAME'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="card-text">'
                'MD.Abdul Aziz'
                '</div>',
                unsafe_allow_html=True
            )

            st.write("")

            st.markdown(
                '<div class="card-heading">'
                'Designation'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="card-text">'
                'Trainer, Co-Lead-AICW'
                '</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="footer-text">'
        'EcoBin AI – Smart Garbage Overflow Detection'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# PREDICTION PAGE
# ============================================================

else:

    st.markdown(
        '<div class="detect-title">'
        '♻️ EcoBin AI'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="detect-subtitle">'
        'AI-Powered Smart Garbage Overflow Detection System'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "← Back to Home",
        key="back"
    ):

        st.session_state.page = "home"
        st.rerun()

    st.write("")

    try:

        model = load_model()

    except Exception as e:

        st.error(
            f"❌ best.pt model load avvaledu: {e}"
        )

        st.info(
            "Make sure best.pt is in the same folder as app.py."
        )

        st.stop()


    # ========================================================
    # IMAGE SECTION
    # ========================================================

    st.markdown(
        '<div class="detection-box-title">'
        '🖼️ Image Detection'
        '</div>',
        unsafe_allow_html=True
    )

    image_upload_col, image_input_col, image_output_col = st.columns(
        3,
        gap="medium"
    )

    with image_upload_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Upload Image'
                '</div>',
                unsafe_allow_html=True
            )

            uploaded_image = st.file_uploader(
                "Choose image",
                type=[
                    "jpg",
                    "jpeg",
                    "png"
                ],
                key="image_upload"
            )

    with image_input_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Input'
                '</div>',
                unsafe_allow_html=True
            )

            input_image = None

            if uploaded_image:

                input_image = Image.open(
                    uploaded_image
                ).convert("RGB")

                st.image(
                    input_image,
                    use_container_width=True
                )

            else:

                st.info(
                    "Upload an image to start prediction."
                )

    with image_output_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Output'
                '</div>',
                unsafe_allow_html=True
            )

            if uploaded_image and input_image is not None:

                if st.button(
                    "🔍 Detect",
                    key="detect_image",
                    use_container_width=True
                ):

                    with st.spinner(
                        "AI is analyzing the image..."
                    ):

                        result, detections = predict_image(
                            input_image,
                            model
                        )

                    st.session_state.image_result = (
                        result,
                        detections
                    )

                if st.session_state.image_result is not None:

                    result, detections = (
                        st.session_state.image_result
                    )

                    display_prediction(
                        result,
                        detections,
                        "Prediction Result"
                    )

            else:

                st.info(
                    "Prediction output will appear here."
                )


    # ========================================================
    # CAMERA SECTION
    # ========================================================

    st.write("")

    st.markdown(
        '<div class="detection-box-title">'
        '📷 Camera Detection'
        '</div>',
        unsafe_allow_html=True
    )

    camera_col, camera_input_col, camera_output_col = st.columns(
        3,
        gap="medium"
    )

    with camera_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Camera'
                '</div>',
                unsafe_allow_html=True
            )

            camera_image = st.camera_input(
                "Capture Image",
                key="camera"
            )

    with camera_input_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Input'
                '</div>',
                unsafe_allow_html=True
            )

            camera_pil = None

            if camera_image:

                camera_pil = Image.open(
                    camera_image
                ).convert("RGB")

                st.image(
                    camera_pil,
                    use_container_width=True
                )

            else:

                st.info(
                    "Camera image will appear here."
                )

    with camera_output_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Output'
                '</div>',
                unsafe_allow_html=True
            )

            if camera_image and camera_pil is not None:

                if st.button(
                    "🔍 Detect",
                    key="detect_camera",
                    use_container_width=True
                ):

                    with st.spinner(
                        "Analyzing camera image..."
                    ):

                        result, detections = predict_image(
                            camera_pil,
                            model
                        )

                    st.session_state.camera_result = (
                        result,
                        detections
                    )

                if st.session_state.camera_result is not None:

                    result, detections = (
                        st.session_state.camera_result
                    )

                    display_prediction(
                        result,
                        detections,
                        "Camera Prediction"
                    )

            else:

                st.info(
                    "Camera prediction will appear here."
                )


    # ========================================================
    # VIDEO / CCTV SECTION
    # ========================================================

    st.write("")
    st.write("")

    st.markdown(
        '<div class="detection-box-title">'
        '🎥 Video / CCTV Detection'
        '</div>',
        unsafe_allow_html=True
    )

    video_upload_col, video_input_col, video_output_col = st.columns(
        3,
        gap="medium"
    )

    with video_upload_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Upload Video'
                '</div>',
                unsafe_allow_html=True
            )

            uploaded_video = st.file_uploader(
                "Choose video",
                type=[
                    "mp4",
                    "avi",
                    "mov",
                    "mkv",
                    "mpeg"
                ],
                key="video_upload"
            )

    with video_input_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Input'
                '</div>',
                unsafe_allow_html=True
            )

            if uploaded_video:

                st.video(
                    uploaded_video
                )

            else:

                st.info(
                    "Upload a CCTV/video file."
                )

    with video_output_col:

        with st.container(border=True):

            st.markdown(
                '<div class="detection-box-title">'
                'Output'
                '</div>',
                unsafe_allow_html=True
            )

            if uploaded_video:

                if st.button(
                    "🎥 Analyze Video",
                    key="detect_video",
                    use_container_width=True
                ):

                    video_bytes = uploaded_video.getvalue()

                    temp_video = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".mp4"
                    )

                    temp_video.write(video_bytes)
                    temp_video.close()

                    try:

                        with st.spinner(
                            "AI is analyzing CCTV video..."
                        ):

                            video_status, best_frame, video_conf = (
                                process_video(
                                    temp_video.name,
                                    model
                                )
                            )

                        st.session_state.video_result = (
                            video_status,
                            best_frame,
                            video_conf
                        )

                    finally:

                        if os.path.exists(
                            temp_video.name
                        ):

                            os.remove(
                                temp_video.name
                            )

                if st.session_state.video_result is not None:

                    video_status, best_frame, video_conf = (
                        st.session_state.video_result
                    )

                    if video_status == "GARBAGE OVERFLOW":

                        if best_frame is not None:

                            st.image(
                                best_frame,
                                caption="Detected Overflow Frame",
                                use_container_width=True
                            )

                        st.markdown(
                            f"""
                            <div class="alert-box">

                            <h3>🚨 Garbage Overflow Detected</h3>

                            <b>Detection:</b> overclass<br><br>

                            <b>Confidence:</b>
                            {video_conf * 100:.2f}%<br><br>

                            <b>📍 Location:</b>
                            {get_location()}<br><br>

                            <b>🕒 Date & Time:</b>
                            {get_current_time()}<br><br>

                            <b>⚠️ Status:</b>
                            Violation Detected

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        generate_alert()

                    elif video_status == "NORMAL":

                        st.markdown(
                            """
                            <div class="normal-box">

                            <h3>✅ No Garbage Overflow Detected</h3>

                            <b>Status:</b>
                            Normal

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.warning(
                            "⚠️ No clear garbage condition "
                            "was detected in the video."
                        )

            else:

                st.info(
                    "Video prediction will appear here."
                )
