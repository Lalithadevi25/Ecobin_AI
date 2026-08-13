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
import requests
import json

from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo

from streamlit_js_eval import streamlit_js_eval


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

defaults = {
    "page": "home",
    "last_alert_time": None,
    "image_result": None,
    "camera_result": None,
    "video_result": None,
    "location_data": None,
    "area_name": None,
    "location_requested": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background: #f4f6fa;
}

.block-container {
    max-width: 1400px;
    padding-top: 25px;
    padding-bottom: 35px;
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


/* ============================================================
   TITLES
   ============================================================ */

.main-title,
.detect-title {

    color: #17345f !important;
    font-weight: 800 !important;
    text-align: center;
}

.main-title {

    font-size: 32px !important;
    margin-bottom: 32px;
}

.detect-title {

    font-size: 32px !important;
    margin-bottom: 5px;
}

.detect-subtitle {

    color: #64748b !important;
    text-align: center;
    font-size: 15px;
    margin-bottom: 25px;
}


/* ============================================================
   HOME
   ============================================================ */

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


/* ============================================================
   CARDS
   ============================================================ */

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


/* ============================================================
   BUTTONS
   ============================================================ */

div.stButton > button {

    width: 100%;
    min-height: 45px;

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


/* ============================================================
   DETECTION TITLES
   ============================================================ */

.detection-box-title {

    color: #17345f !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    margin-bottom: 12px;
}


/* ============================================================
   ALERT BOX
   ============================================================ */

.alert-box {

    background: #fff1f2;
    border: 2px solid #ef4444;
    border-radius: 12px;

    padding: 18px;
    margin-top: 10px;

    color: #991b1b !important;
}


/* ============================================================
   NORMAL BOX
   ============================================================ */

.normal-box {

    background: #f0fdf4;
    border: 2px solid #22c55e;
    border-radius: 12px;

    padding: 18px;
    margin-top: 10px;

    color: #166534 !important;
}


/* ============================================================
   LOCATION BOX
   ============================================================ */

.location-box {

    background: #eff6ff;

    border: 2px solid #3b82f6;

    border-radius: 14px;

    padding: 18px;

    margin-top: 10px;
    margin-bottom: 15px;

    color: #1e3a8a !important;

    text-align: center;
}

.location-title {

    font-size: 18px;
    font-weight: 900;

    color: #17345f !important;

    margin-bottom: 8px;
}

.location-name {

    font-size: 17px;
    font-weight: 800;

    color: #1e40af !important;
}


/* ============================================================
   EMAIL SUCCESS
   ============================================================ */

.email-success {

    background: #dcfce7 !important;

    border: 3px solid #15803d !important;

    border-radius: 14px !important;

    padding: 18px 20px !important;

    margin-top: 14px !important;

    margin-bottom: 10px !important;

    width: 100% !important;

    box-sizing: border-box !important;

    text-align: center !important;
}

.email-success-title {

    color: #14532d !important;

    font-size: 20px !important;

    font-weight: 900 !important;

    margin: 0 0 8px 0 !important;
}

.email-success-text {

    color: #166534 !important;

    font-size: 15px !important;

    font-weight: 700 !important;

    margin: 0 !important;
}


/* ============================================================
   EMAIL ERROR
   ============================================================ */

.email-error {

    background: #fef2f2 !important;

    border: 2px solid #dc2626 !important;

    border-radius: 12px !important;

    padding: 15px !important;

    margin-top: 12px !important;

    color: #991b1b !important;

    font-weight: 700 !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer-text {

    text-align: center;

    color: #64748b;

    margin-top: 35px;

    font-size: 13px;
}


/* ============================================================
   MOBILE
   ============================================================ */

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
""",
    unsafe_allow_html=True
)


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
# DATE & TIME
# ============================================================

def get_current_time():

    india_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return india_time.strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )


# ============================================================
# BROWSER GEOLOCATION
# ============================================================

def request_browser_location():

    try:

        location = streamlit_js_eval(
            js_expressions="""
            new Promise((resolve) => {

                if (!navigator.geolocation) {

                    resolve({
                        "error": {
                            "code": 0,
                            "message": "Geolocation is not supported by this browser."
                        }
                    });

                    return;
                }

                navigator.geolocation.getCurrentPosition(

                    (position) => {

                        resolve({

                            "coords": {

                                "latitude":
                                    position.coords.latitude,

                                "longitude":
                                    position.coords.longitude,

                                "accuracy":
                                    position.coords.accuracy
                            }
                        });

                    },

                    (error) => {

                        resolve({

                            "error": {

                                "code": error.code,

                                "message": error.message
                            }
                        });

                    },

                    {

                        enableHighAccuracy: true,

                        timeout: 15000,

                        maximumAge: 0
                    }
                );

            })
            """,

            key="browser_location_request"
        )

        return location

    except Exception as e:

        return {
            "error": {
                "code": -1,
                "message": str(e)
            }
        }


# ============================================================
# REVERSE GEOCODING
# ============================================================

def reverse_geocode(latitude, longitude):

    try:

        url = (
            "https://nominatim.openstreetmap.org/reverse"
        )

        params = {

            "lat": latitude,

            "lon": longitude,

            "format": "jsonv2",

            "zoom": 18,

            "addressdetails": 1
        }

        headers = {

            "User-Agent":
                "EcoBinAI/1.0 contact: lalithadevi825@gmail.com"
        }

        response = requests.get(

            url,

            params=params,

            headers=headers,

            timeout=10
        )

        if response.status_code != 200:

            return "Area name unavailable"

        data = response.json()

        address = data.get(
            "address",
            {}
        )

        # ----------------------------------------------------
        # Try most useful local area
        # ----------------------------------------------------

        area = (

            address.get("suburb")

            or address.get("neighbourhood")

            or address.get("village")

            or address.get("town")

            or address.get("city_district")

            or address.get("city")

            or address.get("municipality")

        )

        city = (

            address.get("city")

            or address.get("town")

            or address.get("village")

            or address.get("municipality")

        )

        state = address.get(
            "state"
        )

        country = address.get(
            "country"
        )

        parts = []

        if area:
            parts.append(area)

        if city and city != area:
            parts.append(city)

        if state:
            parts.append(state)

        if country:
            parts.append(country)

        if parts:

            return ", ".join(parts)

        display_name = data.get(
            "display_name"
        )

        if display_name:
            return display_name

        return "Area name unavailable"

    except Exception:

        return "Area name unavailable"


# ============================================================
# UPDATE LOCATION
# ============================================================

def update_location():

    location = request_browser_location()

    if not location:

        st.session_state.location_data = None

        st.session_state.area_name = None

        return False

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if "error" in location:

        st.session_state.location_data = None

        st.session_state.area_name = None

        return False

    # --------------------------------------------------------
    # COORDINATES
    # --------------------------------------------------------

    coords = location.get(
        "coords",
        {}
    )

    latitude = coords.get(
        "latitude"
    )

    longitude = coords.get(
        "longitude"
    )

    accuracy = coords.get(
        "accuracy"
    )

    if latitude is None or longitude is None:

        st.session_state.location_data = None

        st.session_state.area_name = None

        return False

    # --------------------------------------------------------
    # SAVE LOCATION
    # --------------------------------------------------------

    st.session_state.location_data = {

        "latitude": latitude,

        "longitude": longitude,

        "accuracy": accuracy
    }

    # --------------------------------------------------------
    # REVERSE GEOCODE
    # --------------------------------------------------------

    area_name = reverse_geocode(
        latitude,
        longitude
    )

    st.session_state.area_name = area_name

    return True


# ============================================================
# LOCATION DISPLAY
# ============================================================

def display_location():

    area = st.session_state.area_name

    if area:

        st.markdown(
            f"""
<div class="location-box">

<div class="location-title">
    📍 Current Live Location
</div>

<div class="location-name">
    {area}
</div>

</div>
""",
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "📍 Location not detected. "
            "Please allow browser location permission."
        )


# ============================================================
# LOCATION BUTTON
# ============================================================

def location_section():

    st.markdown(
        """
<div class="detection-box-title">
    📍 Live Location
</div>
""",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        if st.button(
            "📍 Detect My Location",
            key="location_button",
            use_container_width=True
        ):

            with st.spinner(
                "Detecting your current location..."
            ):

                success = update_location()

            if success:

                st.success(
                    "✅ Location detected successfully!"
                )

            else:

                st.error(
                    "❌ Location could not be detected."
                )

    with col2:

        if st.session_state.area_name:

            display_location()

        else:

            st.info(
                "Click **Detect My Location** and allow browser location permission."
            )


# ============================================================
# GET LOCATION FOR ALERT
# ============================================================

def get_location():

    if st.session_state.area_name:

        return st.session_state.area_name

    return "Location not detected"


# ============================================================
# SEND EMAIL ALERT
# ============================================================

def send_email_alert():

    try:

        sender_email = st.secrets[
            "EMAIL_SENDER"
        ]

        sender_password = st.secrets[
            "EMAIL_PASSWORD"
        ]

        receiver_email = st.secrets[
            "EMAIL_RECEIVER"
        ]

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
overflow

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

            server.send_message(
                message
            )

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

    # --------------------------------------------------------
    # 5 MINUTE COOLDOWN
    # --------------------------------------------------------

    if previous is not None:

        difference = (
            current_dt - previous
        ).total_seconds()

        if difference < 300:

            return

    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    email_sent = send_email_alert()

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if email_sent:

        st.session_state.last_alert_time = (
            current_dt
        )

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
# NORMALIZE CLASS
# ============================================================

def normalize_class_name(name):

    name = str(
        name
    ).lower().strip()

    name = name.replace(
        "_",
        " "
    )

    name = name.replace(
        "-",
        " "
    )

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

    # ========================================================
    # OVERFLOW
    # ========================================================

    overflow_detections = [

        d for d in detections

        if d["class"] in [

            "overflow",
            "overclass",
            "garbage overflow",
            "overflowing",
            "overflowed"

        ]

        and d["confidence"] >= 0.30

    ]

    # ========================================================
    # NORMAL
    # ========================================================

    normal_detections = [

        d for d in detections

        if d["class"] in [

            "normal",
            "normal bin",
            "non overflow",
            "non-overflow"

        ]

    ]

    # ========================================================
    # OVERFLOW FIRST
    # ========================================================

    if overflow_detections:

        best = max(
            overflow_detections,
            key=lambda x: x["confidence"]
        )

        return (
            "GARBAGE OVERFLOW",
            best["confidence"]
        )

    # ========================================================
    # NORMAL
    # ========================================================

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

    image_np = np.array(
        image
    )

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

<b>Detection:</b> overflow<br><br>

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

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        generate_alert()

    # ========================================================
    # NORMAL
    # ========================================================

    elif status == "NORMAL":

        st.markdown(
            f"""
<div class="normal-box">

<h3>✅ No Garbage Overflow Detected</h3>

<b>Detection:</b> normal<br><br>

<b>Confidence:</b>
{confidence * 100:.2f}%<br><br>

<b>📍 Location:</b>
{get_location()}<br><br>

<b>Status:</b>
Normal

</div>
""",
            unsafe_allow_html=True
        )

    # ========================================================
    # NO CLEAR
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

def process_video(
    video_path,
    model
):

    cap = cv2.VideoCapture(
        video_path
    )

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

    # ========================================================
    # OUTPUT FILES
    # ========================================================

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

    # ========================================================
    # WRITER
    # ========================================================

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

    progress = st.progress(
        0
    )

    # ========================================================
    # FRAME LOOP
    # ========================================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # ----------------------------------------------------
        # YOLO
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # COUNTS
        # ----------------------------------------------------

        if status == "GARBAGE OVERFLOW":

            overflow_count += 1

            detection_count += 1

            if confidence > best_overflow_confidence:

                best_overflow_confidence = (
                    confidence
                )

        elif status == "NORMAL":

            normal_count += 1

            detection_count += 1

        # ----------------------------------------------------
        # ANNOTATED
        # ----------------------------------------------------

        annotated_frame = result.plot()

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if status == "GARBAGE OVERFLOW":

            cv2.rectangle(

                annotated_frame,

                (10, 10),

                (520, 80),

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

                (370, 80),

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

        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # WRITE
        # ----------------------------------------------------

        writer.write(
            annotated_frame
        )

        frame_number += 1

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        if total_frames > 0:

            progress.progress(
                min(
                    frame_number / total_frames,
                    1.0
                )
            )

    # ========================================================
    # RELEASE
    # ========================================================

    cap.release()

    writer.release()

    progress.empty()

    # ========================================================
    # H264
    # ========================================================

    try:

        ffmpeg_path = (
            imageio_ffmpeg.get_ffmpeg_exe()
        )

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

        final_video_path = (
            h264_output_path
        )

    except Exception:

        final_video_path = (
            raw_output_path
        )

    # ========================================================
    # READ
    # ========================================================

    try:

        with open(
            final_video_path,
            "rb"
        ) as video_file:

            output_video_bytes = (
                video_file.read()
            )

    except Exception:

        output_video_bytes = None

    # ========================================================
    # CLEANUP
    # ========================================================

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

    # ========================================================
    # FINAL STATUS
    # ========================================================

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
            "🔍 PREDICT",
            key="predict",
            use_container_width=True
        ):

            st.session_state.page = (
                "predict"
            )

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
EcoBin AI is an AI-powered Smart Garbage Overflow
Detection System designed to automatically identify
overflowing garbage bins using computer vision and
YOLOv8 object detection.

The system analyzes images, camera-captured photos,
and CCTV/video files to identify garbage overflow
conditions.

The trained YOLOv8 model classifies garbage-bin
conditions into two classes:

<b>Overflow</b> and <b>Normal</b>.

When an overflow condition is detected, EcoBin AI
automatically generates an alert containing the
current area name, date and time, and violation
status.

The alert can also be sent to the configured email
address.

This system helps reduce manual monitoring effort,
support faster waste-management response, and
improve cleanliness in public and residential areas.
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

    location_section()

    st.write("")
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
    # IMAGE SECTION
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

                st.info(
                    "Upload an image to start prediction."
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

                st.info(
                    "Prediction output will appear here."
                )

    # ========================================================
    # CAMERA
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

                st.info(
                    "Camera image will appear here."
                )

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

                st.info(
                    "Camera prediction will appear here."
                )

    # ========================================================
    # VIDEO
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

                st.info(
                    "Upload a CCTV/video file."
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

                # =================================================
                # VIDEO RESULT
                # =================================================

                if st.session_state.video_result is not None:

                    (
                        video_status,
                        output_video_bytes,
                        video_conf
                    ) = st.session_state.video_result

                    if output_video_bytes is not None:

                        st.markdown(
                            """
<div style="
color:#17345f;
font-size:16px;
font-weight:800;
margin-bottom:10px;
">
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
                    # OVERFLOW
                    # =================================================

                    if video_status == "GARBAGE OVERFLOW":

                        st.markdown(
                            f"""
<div class="alert-box">

<h3>🚨 Garbage Overflow Detected</h3>

<b>Detection:</b> overflow<br><br>

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

                    # =================================================
                    # NORMAL
                    # =================================================

                    elif video_status == "NORMAL":

                        st.markdown(
                            f"""
<div class="normal-box">

<h3>✅ No Garbage Overflow Detected</h3>

<b>📍 Location:</b>
{get_location()}<br><br>

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


# ============================================================
# END
# ============================================================
