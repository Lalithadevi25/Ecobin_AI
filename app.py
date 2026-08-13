import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import tempfile
import os
import smtplib
import subprocess
import imageio_ffmpeg
import urllib.request
import json

from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components


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

st.markdown(
    """
<style>

/* ==========================================================
   MAIN APP
   ========================================================== */

.stApp {
    background: linear-gradient(
        135deg,
        #f8fbff 0%,
        #f0fdf8 50%,
        #f8fbff 100%
    ) !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 28px;
    padding-bottom: 40px;
    padding-left: 5%;
    padding-right: 5%;
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


/* ==========================================================
   TEXT
   ========================================================== */

.main-title,
.detect-title {
    color: #123b63 !important;
    -webkit-text-fill-color: #123b63 !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    text-align: center !important;
}

.main-title {
    margin-bottom: 32px;
}

.detect-title {
    margin-bottom: 5px;
}

.detect-subtitle {
    color: #526579 !important;
    -webkit-text-fill-color: #526579 !important;
    text-align: center !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 25px;
}

.aicw-text {
    color: #123b63 !important;
    -webkit-text-fill-color: #123b63 !important;
    font-size: 25px !important;
    font-weight: 900 !important;
    line-height: 1.55;
}

.capstone-text {
    color: #276749 !important;
    -webkit-text-fill-color: #276749 !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    margin-top: 42px;
}

.description-title {
    color: #123b63 !important;
    -webkit-text-fill-color: #123b63 !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    margin-bottom: 12px;
}


/* ==========================================================
   NORMAL MARKDOWN TEXT
   ========================================================== */

.stMarkdown,
.stMarkdown p,
.stMarkdown li,
.stMarkdown span {
    color: #263746 !important;
    -webkit-text-fill-color: #263746 !important;
}


/* ==========================================================
   DESCRIPTION
   ========================================================== */

.description-box {
    background: #ffffff !important;
    border: 1px solid #d8e3ec !important;
    border-radius: 16px !important;
    padding: 24px !important;
    color: #263746 !important;
    font-size: 15px !important;
    line-height: 1.8 !important;
}


/* ==========================================================
   STREAMLIT CONTAINERS / CARDS
   ========================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.96) !important;
    border: 1px solid #d7e4ed !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 25px rgba(20, 55, 85, 0.08) !important;
    padding: 10px !important;
}


/* ==========================================================
   CARD HEADINGS
   ========================================================== */

.card-heading {
    color: #17466e !important;
    -webkit-text-fill-color: #17466e !important;
    font-size: 15px !important;
    font-weight: 900 !important;
    margin-bottom: 16px;
}

.card-text {
    color: #405364 !important;
    -webkit-text-fill-color: #405364 !important;
    font-size: 14px !important;
    line-height: 2.2 !important;
}


/* ==========================================================
   DETECTION TITLES
   ========================================================== */

.detection-box-title {
    color: #124f45 !important;
    -webkit-text-fill-color: #124f45 !important;
    font-size: 19px !important;
    font-weight: 900 !important;
    margin-bottom: 13px;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

div.stButton > button {
    width: 100%;
    min-height: 46px;
    background: #ffffff !important;
    color: #17466e !important;
    -webkit-text-fill-color: #17466e !important;
    border: 2px solid #cbdbe7 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    box-shadow: 0 3px 10px rgba(20,55,85,0.05) !important;
}

div.stButton > button:hover {
    border-color: #16866f !important;
    color: #12614f !important;
    -webkit-text-fill-color: #12614f !important;
    background: #f0fdf9 !important;
}


/* ==========================================================
   FILE UPLOADER
   ========================================================== */

[data-testid="stFileUploader"] {
    background: #f8fbfd !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] section {
    background: #f8fbfd !important;
    border: 1px dashed #9db8c9 !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] label {
    color: #29465b !important;
    -webkit-text-fill-color: #29465b !important;
    font-weight: 700 !important;
}

[data-testid="stFileUploader"] small {
    color: #607586 !important;
    -webkit-text-fill-color: #607586 !important;
}


/* ==========================================================
   CAMERA
   ========================================================== */

[data-testid="stCameraInput"] {
    border-radius: 12px !important;
}


/* ==========================================================
   INPUT / OUTPUT PLACEHOLDER BOX
   ========================================================== */

/* Streamlit info boxes */
div[data-testid="stAlert"] {
    background: #eef7ff !important;
    border: 1px solid #9ec5e6 !important;
    border-radius: 12px !important;
    opacity: 1 !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] span {
    color: #24506e !important;
    -webkit-text-fill-color: #24506e !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}


/* ==========================================================
   CUSTOM PLACEHOLDER
   ========================================================== */

.placeholder-box {
    background: linear-gradient(
        135deg,
        #eef8ff,
        #eefcf7
    ) !important;

    border: 1px solid #b8d9e5 !important;
    border-radius: 12px !important;

    min-height: 82px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    padding: 18px !important;
    margin-top: 8px !important;

    color: #31566e !important;
    -webkit-text-fill-color: #31566e !important;

    font-size: 14px !important;
    font-weight: 700 !important;

    text-align: center !important;
}


/* ==========================================================
   ALERT BOX
   ========================================================== */

.alert-box {
    background: linear-gradient(
        135deg,
        #fff5f5,
        #fffafa
    ) !important;

    border: 3px solid #ef4444 !important;
    border-radius: 15px !important;

    padding: 20px !important;
    margin-top: 12px !important;

    color: #7f1d1d !important;
    -webkit-text-fill-color: #7f1d1d !important;

    box-shadow: 0 8px 22px rgba(239,68,68,0.12) !important;
}

.alert-box h3,
.alert-box b,
.alert-box {
    color: #7f1d1d !important;
    -webkit-text-fill-color: #7f1d1d !important;
    opacity: 1 !important;
}


/* ==========================================================
   NORMAL BOX
   ========================================================== */

.normal-box {
    background: linear-gradient(
        135deg,
        #f0fdf4,
        #f7fff9
    ) !important;

    border: 3px solid #22c55e !important;
    border-radius: 15px !important;

    padding: 20px !important;
    margin-top: 12px !important;

    color: #166534 !important;
    -webkit-text-fill-color: #166534 !important;

    box-shadow: 0 8px 22px rgba(34,197,94,0.10) !important;
}

.normal-box h3,
.normal-box b,
.normal-box {
    color: #166534 !important;
    -webkit-text-fill-color: #166534 !important;
    opacity: 1 !important;
}


/* ==========================================================
   EMAIL SUCCESS
   ========================================================== */

.email-success {
    background: linear-gradient(
        135deg,
        #dcfce7,
        #ecfdf5
    ) !important;

    border: 3px solid #16a34a !important;
    border-radius: 15px !important;

    padding: 20px !important;
    margin-top: 15px !important;
    margin-bottom: 12px !important;

    width: 100% !important;
    box-sizing: border-box !important;

    text-align: center !important;

    box-shadow: 0 8px 22px rgba(22,163,74,0.12) !important;

    opacity: 1 !important;
}

.email-success-title {
    color: #14532d !important;
    -webkit-text-fill-color: #14532d !important;

    font-size: 19px !important;
    font-weight: 900 !important;

    margin: 0 0 8px 0 !important;
    line-height: 1.5 !important;

    opacity: 1 !important;
}

.email-success-text {
    color: #166534 !important;
    -webkit-text-fill-color: #166534 !important;

    font-size: 15px !important;
    font-weight: 800 !important;

    margin: 0 !important;
    line-height: 1.6 !important;

    opacity: 1 !important;
}


/* ==========================================================
   EMAIL ERROR
   ========================================================== */

.email-error {
    background: #fff1f2 !important;
    border: 2px solid #dc2626 !important;
    border-radius: 12px !important;

    padding: 15px !important;
    margin-top: 12px !important;

    color: #991b1b !important;
    -webkit-text-fill-color: #991b1b !important;

    font-weight: 800 !important;
    opacity: 1 !important;
}


/* ==========================================================
   LOCATION CARD
   ========================================================== */

.location-card {
    background: linear-gradient(
        135deg,
        #effcf8,
        #f0f9ff
    ) !important;

    border: 2px solid #63b8a6 !important;
    border-radius: 15px !important;

    padding: 18px !important;
    margin-top: 15px !important;

    box-shadow: 0 6px 18px rgba(20,120,100,0.08) !important;
}

.location-title {
    color: #075e54 !important;
    -webkit-text-fill-color: #075e54 !important;

    font-size: 18px !important;
    font-weight: 900 !important;

    margin-bottom: 8px !important;
}

.location-text {
    color: #28545a !important;
    -webkit-text-fill-color: #28545a !important;

    font-size: 14px !important;
    font-weight: 700 !important;

    line-height: 1.7 !important;
}


/* ==========================================================
   DETECTION DETAILS
   ========================================================== */

.details-title {
    color: #173f62 !important;
    -webkit-text-fill-color: #173f62 !important;

    font-size: 17px !important;
    font-weight: 900 !important;

    margin-top: 18px !important;
    margin-bottom: 10px !important;
}

.detail-item {
    background: #f7fafc !important;

    border-left: 4px solid #3b82f6 !important;

    border-radius: 7px !important;

    padding: 9px 12px !important;
    margin-bottom: 7px !important;

    color: #334e68 !important;
    -webkit-text-fill-color: #334e68 !important;

    font-size: 14px !important;
    font-weight: 700 !important;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer-text {
    text-align: center;

    color: #607586 !important;
    -webkit-text-fill-color: #607586 !important;

    margin-top: 35px;

    font-size: 13px;
    font-weight: 600;
}


/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media(max-width: 900px) {

    .block-container {
        padding-left: 4%;
        padding-right: 4%;
    }

    .main-title,
    .detect-title {
        font-size: 25px !important;
    }

    .aicw-text {
        font-size: 21px !important;
    }

    .capstone-text {
        font-size: 19px !important;
    }

    .email-success-title {
        font-size: 17px !important;
    }

    .email-success-text {
        font-size: 14px !important;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD MODEL
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
# APPROXIMATE LOCATION USING IP
# ============================================================

def get_ip_location():

    try:

        url = "https://ipapi.co/json/"

        with urllib.request.urlopen(
            url,
            timeout=5
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country_name", "")

        if city:

            return (
                f"{city}, {region}, {country}"
            )

    except Exception:
        pass

    return "Location not available"


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

    return get_ip_location()


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
# LIVE LOCATION UI
# ============================================================

def show_live_location():

    st.markdown(
        """
<div class="location-card">

<div class="location-title">
📍 Live Location Access
</div>

<div class="location-text">
Allow browser location permission to get the current
device coordinates.
</div>

</div>
""",
        unsafe_allow_html=True
    )

    components.html(
        """
<!DOCTYPE html>

<html>

<head>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: transparent;
}

.location-container {
    background: #ffffff;
    border: 1px solid #b8d9d0;
    border-radius: 12px;
    padding: 14px;
    margin-top: 8px;
}

button {
    background: #087f5b;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 18px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #066a4c;
}

#status {
    margin-top: 12px;
    color: #29465b;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.6;
}

a {
    color: #1769aa;
    font-weight: bold;
}

</style>

</head>

<body>

<div class="location-container">

<button onclick="getLocation()">
📍 Get My Live Location
</button>

<div id="status">
Click the button and allow location permission.
</div>

</div>


<script>

function getLocation() {

    const status = document.getElementById("status");

    if (!navigator.geolocation) {

        status.innerHTML =
            "❌ Geolocation is not supported by this browser.";

        return;
    }

    status.innerHTML =
        "⏳ Requesting your location permission...";

    navigator.geolocation.getCurrentPosition(

        function(position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;

            const accuracy =
                position.coords.accuracy;

            const mapURL =
                "https://www.google.com/maps?q="
                + latitude
                + ","
                + longitude;

            status.innerHTML =
                "✅ <b>Live Location Detected</b><br><br>" +

                "Latitude: "
                + latitude.toFixed(6)
                + "<br>" +

                "Longitude: "
                + longitude.toFixed(6)
                + "<br>" +

                "Accuracy: approximately "
                + Math.round(accuracy)
                + " meters<br><br>" +

                "<a href='"
                + mapURL
                + "' target='_blank'>"
                + "🗺️ Open Location in Google Maps"
                + "</a>";
        },

        function(error) {

            if (error.code === 1) {

                status.innerHTML =
                    "❌ Location permission denied. " +
                    "Please allow location access in your browser.";

            }

            else if (error.code === 2) {

                status.innerHTML =
                    "❌ Location unavailable. " +
                    "Please check GPS/location services.";

            }

            else if (error.code === 3) {

                status.innerHTML =
                    "❌ Location request timed out. " +
                    "Please try again.";

            }

            else {

                status.innerHTML =
                    "❌ Unable to get your location.";

            }

        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }

    );

}

</script>

</body>

</html>
""",
        height=175
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
            "🚨 EcoBin AI - Garbage Overflow Alert"
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

        st.markdown(
            f"""
<div class="email-error">
❌ Email alert failed: {str(e)}
</div>
""",
            unsafe_allow_html=True
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

    email_sent = send_email_alert()

    if email_sent:

        st.session_state.last_alert_time = current_dt

        st.markdown(
            """
<div class="email-success">

<div class="email-success-title">
📧 ALERT EMAIL SENT SUCCESSFULLY
</div>

<div class="email-success-text">
The garbage overflow alert has been successfully
sent to the configured email address.
</div>

</div>
""",
            unsafe_allow_html=True
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
# EXTRACT DETECTIONS
# ============================================================

def extract_detections(result):

    detections = []

    if result.boxes is None:

        return detections

    for box in result.boxes:

        class_id = int(
            box.cls[0]
        )

        confidence = float(
            box.conf[0]
        )

        class_name = normalize_class_name(
            result.names[class_id]
        )

        detections.append(
            {
                "class": class_name,
                "confidence": confidence
            }
        )

    return detections


# ============================================================
# FINAL PREDICTION
# ============================================================

def get_final_prediction(detections):

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

    detections = extract_detections(
        result
    )

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
        f"""
<div class="detection-box-title">
{title}
</div>
""",
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


    # ========================================================
    # OVERFLOW
    # ========================================================

    if status == "GARBAGE OVERFLOW":

        st.markdown(
            f"""
<div class="alert-box">

<h3>🚨 Garbage Overflow Detected</h3>

<b>Detection:</b> overclass

<br><br>

<b>Confidence:</b>
{confidence * 100:.2f}%

<br><br>

<b>📍 Location:</b>
{get_location()}

<br><br>

<b>🕒 Date & Time:</b>
{get_current_time()}

<br><br>

<b>⚠️ Status:</b>
Violation Detected

</div>
""",
            unsafe_allow_html=True
        )

        generate_alert()


    # ========================================================
    # NORMAL
    # ========================================================

    elif status == "NORMAL":

        st.markdown(
            f"""
<div class="normal-box">

<h3>✅ No Garbage Overflow Detected</h3>

<b>Detection:</b> normal

<br><br>

<b>Confidence:</b>
{confidence * 100:.2f}%

<br><br>

<b>Status:</b>
Normal

</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # NO DETECTION
    # ========================================================

    else:

        st.warning(
            "⚠️ No clear garbage condition detected. "
            "Please try another image/video."
        )


    # ========================================================
    # DETAILS
    # ========================================================

    if detections:

        st.markdown(
            """
<div class="details-title">
🔎 Detection Details
</div>
""",
            unsafe_allow_html=True
        )

        for detection in detections:

            st.markdown(
                f"""
<div class="detail-item">
• {detection['class']} —
{detection['confidence'] * 100:.2f}%
</div>
""",
                unsafe_allow_html=True
            )


# ============================================================
# PROCESS VIDEO
# ============================================================

def process_video(video_path, model):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        return (
            "NO CLEAR DETECTION",
            None,
            0.0
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:
        fps = 25

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    raw_output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    raw_output_path = raw_output.name
    raw_output.close()

    h264_output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    h264_output_path = h264_output.name
    h264_output.close()

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        raw_output_path,
        fourcc,
        fps,
        (width, height)
    )

    frame_number = 0

    overflow_count = 0
    normal_count = 0
    detection_count = 0

    best_overflow_confidence = 0.0

    progress = st.progress(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

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

        elif status == "NORMAL":

            normal_count += 1
            detection_count += 1

        annotated_frame = result.plot()

        if status == "GARBAGE OVERFLOW":

            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (540, 80),
                (0, 0, 255),
                -1
            )

            cv2.putText(
                annotated_frame,
                "GARBAGE OVERFLOW DETECTED",
                (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.80,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        elif status == "NORMAL":

            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (300, 80),
                (0, 150, 0),
                -1
            )

            cv2.putText(
                annotated_frame,
                "NORMAL",
                (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.80,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        else:

            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (390, 80),
                (80, 80, 80),
                -1
            )

            cv2.putText(
                annotated_frame,
                "NO CLEAR DETECTION",
                (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        if confidence > 0:

            cv2.putText(
                annotated_frame,
                f"Confidence: {confidence * 100:.2f}%",
                (15, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        writer.write(
            annotated_frame
        )

        frame_number += 1

        if total_frames > 0:

            progress.progress(
                min(
                    frame_number / total_frames,
                    1.0
                )
            )

    cap.release()
    writer.release()
    progress.empty()

    try:

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        command = [

            ffmpeg_path,

            "-y",

            "-i",
            raw_output_path,

            "-c:v",
            "libx264",

            "-preset",
            "fast",

            "-crf",
            "23",

            "-pix_fmt",
            "yuv420p",

            "-movflags",
            "+faststart",

            h264_output_path
        ]

        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        final_video_path = h264_output_path

    except Exception:

        final_video_path = raw_output_path

    try:

        with open(
            final_video_path,
            "rb"
        ) as video_file:

            output_video_bytes = video_file.read()

    except Exception:

        output_video_bytes = None

    try:

        if os.path.exists(
            raw_output_path
        ):

            os.remove(
                raw_output_path
            )

        if os.path.exists(
            h264_output_path
        ):

            os.remove(
                h264_output_path
            )

    except Exception:

        pass

    if detection_count == 0:

        return (
            "NO CLEAR DETECTION",
            output_video_bytes,
            0.0
        )

    if overflow_count > 0:

        return (
            "GARBAGE OVERFLOW",
            output_video_bytes,
            best_overflow_confidence
        )

    return (
        "NORMAL",
        output_video_bytes,
        0.0
    )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.markdown(
        """
<div class="main-title">
♻️ EcoBin AI – Smart Garbage Overflow Detection
</div>
""",
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns(
        [0.38, 0.62],
        gap="large"
    )


    # ========================================================
    # LEFT
    # ========================================================

    with left_col:

        st.markdown(
            """
<div class="aicw-text">
AI Career for Women
<br>
(AICW)
</div>
""",
            unsafe_allow_html=True
        )

        st.markdown(
            """
<div class="capstone-text">
Capstone Project
</div>
""",
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


    # ========================================================
    # RIGHT
    # ========================================================

    with right_col:

        st.markdown(
            """
<div class="description-title">
Project Description
</div>
""",
            unsafe_allow_html=True
        )

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div style="
color:#263746 !important;
font-size:15px;
line-height:1.8;
">

EcoBin AI is an AI-powered Smart Garbage Overflow
Detection System designed to automatically identify
overflowing garbage bins using computer vision and
YOLOv8 object detection.

The system analyzes images, camera-captured photos,
and CCTV/video files to identify garbage overflow
conditions. The trained YOLOv8 model classifies the
detected garbage condition into two classes:
<b style="color:#b42318;">overclass</b> and
<b style="color:#166534;">normal</b>.

When an overflow condition is detected, EcoBin AI
automatically generates an alert containing the
location, date and time, and violation status.
The alert is also sent to the configured user's
email address.

This system helps reduce manual monitoring effort,
support faster waste-management response, and
improve cleanliness in public and residential areas.

</div>
""",
                unsafe_allow_html=True
            )


    st.write("")
    st.write("")


    # ========================================================
    # TEAM
    # ========================================================

    team_col, gmail_col, guide_col = st.columns(
        [1.25, 1.25, 0.75],
        gap="large"
    )


    with team_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="card-heading">
TEAM MEMBERS
</div>
""",
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

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="card-heading">
GMAIL
</div>
""",
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

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="card-heading">
GUIDE NAME
</div>
""",
                unsafe_allow_html=True
            )

            st.markdown(
                """
<div class="card-text">
MD.Abdul Aziz
</div>
""",
                unsafe_allow_html=True
            )

            st.write("")

            st.markdown(
                """
<div class="card-heading">
Designation
</div>
""",
                unsafe_allow_html=True
            )

            st.markdown(
                """
<div class="card-text">
Trainer, Co-Lead-AICW
</div>
""",
                unsafe_allow_html=True
            )


    st.markdown(
        """
<div class="footer-text">
EcoBin AI – Smart Garbage Overflow Detection
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# PREDICTION PAGE
# ============================================================

else:

    st.markdown(
        """
<div class="detect-title">
♻️ EcoBin AI
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="detect-subtitle">
AI-Powered Smart Garbage Overflow Detection System
</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # BACK
    # ========================================================

    if st.button(
        "← Back to Home",
        key="back"
    ):

        st.session_state.page = "home"

        st.rerun()


    st.write("")


    # ========================================================
    # LIVE LOCATION
    # ========================================================

    show_live_location()

    st.write("")


    # ========================================================
    # MODEL
    # ========================================================

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
    # IMAGE DETECTION
    # ========================================================

    st.markdown(
        """
<div class="detection-box-title">
🖼️ Image Detection
</div>
""",
        unsafe_allow_html=True
    )

    image_upload_col, image_input_col, image_output_col = st.columns(
        3,
        gap="medium"
    )


    # ========================================================
    # IMAGE UPLOAD
    # ========================================================

    with image_upload_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Upload Image
</div>
""",
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


    # ========================================================
    # IMAGE INPUT
    # ========================================================

    with image_input_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Input
</div>
""",
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

                st.markdown(
                    """
<div class="placeholder-box">
📷 Upload an image to see the input here.
</div>
""",
                    unsafe_allow_html=True
                )


    # ========================================================
    # IMAGE OUTPUT
    # ========================================================

    with image_output_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Output
</div>
""",
                unsafe_allow_html=True
            )

            if uploaded_image and input_image is not None:

                if st.button(
                    "🔍 Detect",
                    key="detect_image",
                    use_container_width=True
                ):

                    with st.spinner(
                        "🤖 AI is analyzing the image..."
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

                st.markdown(
                    """
<div class="placeholder-box">
🎯 Prediction output will appear here.
</div>
""",
                    unsafe_allow_html=True
                )


    # ========================================================
    # CAMERA SECTION
    # ========================================================

    st.write("")

    st.markdown(
        """
<div class="detection-box-title">
📷 Camera Detection
</div>
""",
        unsafe_allow_html=True
    )

    camera_col, camera_input_col, camera_output_col = st.columns(
        3,
        gap="medium"
    )


    # ========================================================
    # CAMERA
    # ========================================================

    with camera_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Camera
</div>
""",
                unsafe_allow_html=True
            )

            camera_image = st.camera_input(
                "Capture Image",
                key="camera"
            )


    # ========================================================
    # CAMERA INPUT
    # ========================================================

    with camera_input_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Input
</div>
""",
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

                st.markdown(
                    """
<div class="placeholder-box">
📷 Camera image will appear here.
</div>
""",
                    unsafe_allow_html=True
                )


    # ========================================================
    # CAMERA OUTPUT
    # ========================================================

    with camera_output_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Output
</div>
""",
                unsafe_allow_html=True
            )

            if camera_image and camera_pil is not None:

                if st.button(
                    "🔍 Detect",
                    key="detect_camera",
                    use_container_width=True
                ):

                    with st.spinner(
                        "🤖 Analyzing camera image..."
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

                st.markdown(
                    """
<div class="placeholder-box">
🎯 Camera prediction will appear here.
</div>
""",
                    unsafe_allow_html=True
                )


    # ========================================================
    # VIDEO SECTION
    # ========================================================

    st.write("")
    st.write("")

    st.markdown(
        """
<div class="detection-box-title">
🎥 Video / CCTV Detection
</div>
""",
        unsafe_allow_html=True
    )

    video_upload_col, video_input_col, video_output_col = st.columns(
        3,
        gap="medium"
    )


    # ========================================================
    # VIDEO UPLOAD
    # ========================================================

    with video_upload_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Upload Video
</div>
""",
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


    # ========================================================
    # VIDEO INPUT
    # ========================================================

    with video_input_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Input
</div>
""",
                unsafe_allow_html=True
            )

            if uploaded_video:

                st.video(
                    uploaded_video
                )

            else:

                st.markdown(
                    """
<div class="placeholder-box">
🎥 Upload a CCTV/video file to see the input here.
</div>
""",
                    unsafe_allow_html=True
                )


    # ========================================================
    # VIDEO OUTPUT
    # ========================================================

    with video_output_col:

        with st.container(
            border=True
        ):

            st.markdown(
                """
<div class="detection-box-title">
Output
</div>
""",
                unsafe_allow_html=True
            )

            if uploaded_video:

                if st.button(
                    "🎥 Analyze Video",
                    key="detect_video",
                    use_container_width=True
                ):

                    video_bytes = (
                        uploaded_video.getvalue()
                    )

                    temp_video = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".mp4"
                    )

                    temp_video.write(
                        video_bytes
                    )

                    temp_video.close()

                    try:

                        with st.spinner(
                            "🤖 AI is analyzing CCTV video..."
                        ):

                            (
                                video_status,
                                output_video_bytes,
                                video_conf
                            ) = process_video(
                                temp_video.name,
                                model
                            )

                        st.session_state.video_result = (
                            video_status,
                            output_video_bytes,
                            video_conf
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Video processing failed: {e}"
                        )

                    finally:

                        if os.path.exists(
                            temp_video.name
                        ):

                            os.remove(
                                temp_video.name
                            )


                if st.session_state.video_result is not None:

                    (
                        video_status,
                        output_video_bytes,
                        video_conf
                    ) = st.session_state.video_result


                    # =================================================
                    # OUTPUT VIDEO
                    # =================================================

                    if output_video_bytes is not None:

                        st.markdown(
                            """
<div class="detection-box-title">
🎬 AI Processed Output Video
</div>
""",
                            unsafe_allow_html=True
                        )

                        st.video(
                            output_video_bytes
                        )

                    else:

                        st.error(
                            "❌ Output video could not be generated."
                        )


                    # =================================================
                    # VIDEO OVERFLOW
                    # =================================================

                    if video_status == "GARBAGE OVERFLOW":

                        st.markdown(
                            f"""
<div class="alert-box">

<h3>🚨 Garbage Overflow Detected</h3>

<b>Detection:</b> overclass

<br><br>

<b>Confidence:</b>
{video_conf * 100:.2f}%

<br><br>

<b>📍 Location:</b>
{get_location()}

<br><br>

<b>🕒 Date & Time:</b>
{get_current_time()}

<br><br>

<b>⚠️ Status:</b>
Violation Detected

</div>
""",
                            unsafe_allow_html=True
                        )

                        generate_alert()


                    # =================================================
                    # VIDEO NORMAL
                    # =================================================

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


                    # =================================================
                    # NO DETECTION
                    # =================================================

                    else:

                        st.warning(
                            "⚠️ No clear garbage condition "
                            "was detected in the video."
                        )

            else:

                st.markdown(
                    """
<div class="placeholder-box">
🎯 Video prediction will appear here.
</div>
""",
                    unsafe_allow_html=True
                )
