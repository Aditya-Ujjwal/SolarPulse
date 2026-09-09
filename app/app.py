import os
import sys
import json
from datetime import date, time

import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SolarPulse | Prediction App",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ML_DIR = os.path.join(PROJECT_ROOT, "ml")
PYTHON_DIR = os.path.join(PROJECT_ROOT, "python")

MODEL_PATH = os.path.join(ML_DIR, "solar_generation_model.pkl")
CONFIG_PATH = os.path.join(ML_DIR, "detector_config.json")

if PYTHON_DIR not in sys.path:
    sys.path.insert(0, PYTHON_DIR)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(42,157,143,.08), transparent 30%),
            radial-gradient(circle at 100% 10%, rgba(38,70,83,.07), transparent 28%),
            #f5f7fa;
        color:#1f2937;
    }
    .main .block-container {
        max-width:1180px;
        padding-top:1.8rem;
        padding-bottom:3rem;
    }
    .brand-row {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:1rem;
        padding:.25rem 0 1.1rem;
    }
    .brand-left { display:flex; align-items:center; gap:.85rem; }
    .brand-icon {
        width:48px; height:48px; border-radius:14px;
        display:flex; align-items:center; justify-content:center;
        background:linear-gradient(135deg,#0f766e,#2a9d8f);
        color:#fff; font-size:1.55rem;
        box-shadow:0 10px 25px rgba(15,118,110,.22);
    }
    .brand-title {
        margin:0; font-size:2rem; line-height:1;
        font-weight:800; letter-spacing:.02em; color:#173042;
    }
    .brand-subtitle { margin-top:.35rem; font-size:.94rem; color:#64748b; }
    .status-pill {
        padding:.45rem .8rem; border-radius:999px;
        font-size:.78rem; font-weight:700;
        color:#0f766e; background:#e6f6f3; border:1px solid #b8e3dc;
    }
    .section-card {
        background:rgba(255,255,255,.94);
        border:1px solid #e5e7eb; border-radius:18px;
        padding:1.15rem 1.25rem 1.25rem;
        margin:.7rem 0 1rem;
        box-shadow:0 8px 25px rgba(15,23,42,.05);
    }
    .section-title {
        margin:0 0 .15rem; font-size:1.02rem;
        font-weight:800; letter-spacing:.06em;
        text-transform:uppercase; color:#173042;
    }
    .section-caption { margin:0 0 .95rem; font-size:.84rem; color:#64748b; }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stTimeInput"] label {
    font-size: .82rem !important;
    font-weight: 700 !important;
    color: #334155 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input {
    border-radius: 10px !important;
    border: 1px solid #d7dee7 !important;
    background: #ffffff !important;
    color: #173042 !important;
    -webkit-text-fill-color: #173042 !important;
    caret-color: #173042 !important;
    }

    div[data-baseweb="select"] * {
    color: #173042 !important;
    }

    div[data-testid="stNumberInput"] input::placeholder,
    div[data-testid="stDateInput"] input::placeholder,
    div[data-testid="stTimeInput"] input::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
    }

    div[data-baseweb="select"] > div:hover,
    div[data-testid="stNumberInput"] input:hover,
    div[data-testid="stDateInput"] input:hover,
    div[data-testid="stTimeInput"] input:hover {
    border-color: #2a9d8f !important;
    }
    .stButton > button {
        width:100%; min-height:52px;
        border:0 !important; border-radius:12px !important;
        background:linear-gradient(135deg,#0f766e,#2a9d8f) !important;
        color:#fff !important; font-size:.98rem !important;
        font-weight:800 !important; letter-spacing:.02em;
        box-shadow:0 12px 28px rgba(42,157,143,.22);
        transition:all .2s ease;
    }
    .stButton > button:hover {
        transform:translateY(-1px);
        box-shadow:0 16px 32px rgba(42,157,143,.28);
    }
    .prediction-hero {
        margin-top:1rem; border-radius:20px; padding:1.6rem 1.5rem;
        background:linear-gradient(135deg,rgba(23,48,66,.98),rgba(15,118,110,.96));
        color:#fff; box-shadow:0 18px 40px rgba(15,23,42,.18);
    }
    .prediction-label {
        font-size:.78rem; letter-spacing:.12em; font-weight:800;
        opacity:.78; text-transform:uppercase;
    }
    .prediction-value {
        margin-top:.35rem; font-size:3.15rem; line-height:1; font-weight:850;
    }
    .prediction-note { margin-top:.5rem; font-size:.88rem; opacity:.8; }
    .metric-card {
        background:#fff; border:1px solid #e6ebf0; border-radius:16px;
        padding:1rem; min-height:108px;
        box-shadow:0 8px 22px rgba(15,23,42,.04);
    }
    .metric-label {
        font-size:.78rem; color:#64748b; font-weight:700;
        text-transform:uppercase; letter-spacing:.04em;
    }
    .metric-value { margin-top:.35rem; font-size:1.55rem; font-weight:800; color:#173042; }
    .status-normal {
        border-left:5px solid #2a9d8f; background:#eefaf7; color:#14532d;
        border-radius:12px; padding:.95rem 1rem; font-weight:700;
    }
    .status-warning {
        border-left:5px solid #e09f3e; background:#fff8e7; color:#7c4a03;
        border-radius:12px; padding:.95rem 1rem; font-weight:700;
    }
    .status-critical {
        border-left:5px solid #c2410c; background:#fff1ed; color:#7c2d12;
        border-radius:12px; padding:.95rem 1rem; font-weight:700;
    }
    .status-na {
        border-left:5px solid #64748b; background:#f1f5f9; color:#334155;
        border-radius:12px; padding:.95rem 1rem; font-weight:700;
    }
    .site-info-grid {
        display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
        gap:.65rem; margin-top:.5rem;
    }
    .site-info-item {
        background:#f8fafc; border:1px solid #e8edf2; border-radius:12px;
        padding:.7rem .75rem;
    }
    .site-info-label {
        font-size:.72rem; color:#64748b; font-weight:700;
        text-transform:uppercase;
    }
    .site-info-value {
        margin-top:.15rem; font-size:.9rem; color:#173042;
        font-weight:700; word-break:break-word;
    }
    .footer {
        margin-top:2rem; padding-top:1rem; border-top:1px solid #dde4eb;
        text-align:center; color:#94a3b8; font-size:.76rem;
    }
    @media (max-width:850px) {
        .brand-row { flex-direction:column; align-items:flex-start; }
        .site-info-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        .prediction-value { font-size:2.45rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_detector_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Detector configuration not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_sites():
    from database import engine
    query = """
        SELECT
            CampusKey,
            SiteKey,
            kWp,
            Number_of_Panels,
            Panel,
            Inverter,
            Optimizers,
            Latitude,
            Longitude
        FROM solar_sites
        ORDER BY CampusKey, SiteKey
    """
    return pd.read_sql(query, engine)

def create_prediction_features(
    campus_key,
    site_key,
    prediction_date,
    prediction_time,
    air_temperature,
    apparent_temperature,
    dew_point,
    humidity,
    wind_speed,
    wind_direction,
):
    timestamp = pd.Timestamp.combine(prediction_date, prediction_time)
    hour = timestamp.hour
    day_of_week = timestamp.dayofweek
    month = timestamp.month
    day_of_year = timestamp.dayofyear
    is_weekend = int(day_of_week >= 5)

    return pd.DataFrame({
        "CampusKey": [campus_key],
        "SiteKey": [site_key],
        "AirTemperature": [air_temperature],
        "ApparentTemperature": [apparent_temperature],
        "DewPointTemperature": [dew_point],
        "RelativeHumidity": [humidity],
        "WindSpeed": [wind_speed],
        "WindDirection_sin": [np.sin(np.radians(wind_direction))],
        "WindDirection_cos": [np.cos(np.radians(wind_direction))],
        "Hour_sin": [np.sin(2 * np.pi * hour / 24)],
        "Hour_cos": [np.cos(2 * np.pi * hour / 24)],
        "DayOfYear_sin": [np.sin(2 * np.pi * day_of_year / 365.25)],
        "DayOfYear_cos": [np.cos(2 * np.pi * day_of_year / 365.25)],
        "DayOfWeek": [day_of_week],
        "Month": [month],
        "IsWeekend": [is_weekend],
    })

def performance_assessment(
    actual_generation,
    expected_generation,
    performance_floor,
    warning_threshold,
    critical_threshold,
):
    if expected_generation < performance_floor:
        return None, None, "Not Applicable"

    deviation = (
        (actual_generation - expected_generation)
        / expected_generation
        * 100
    )
    ratio = actual_generation / expected_generation

    if deviation <= critical_threshold:
        status = "Critical"
    elif deviation <= warning_threshold:
        status = "Warning"
    else:
        status = "Normal"

    return float(deviation), float(ratio), status

try:
    model = load_model()
    detector_config = load_detector_config()
    sites = load_sites()
except Exception as exc:
    st.error("SolarPulse could not initialize correctly.")
    st.code(str(exc))
    st.stop()

PERFORMANCE_FLOOR = float(detector_config["performance_floor"])
WARNING_THRESHOLD = float(detector_config["warning_threshold"])
CRITICAL_THRESHOLD = float(detector_config["critical_threshold"])

st.markdown(
    """
    <div class="brand-row">
        <div class="brand-left">
            <div class="brand-icon">☀️</div>
            <div>
                <div class="brand-title">SOLARPULSE</div>
                <div class="brand-subtitle">
                    Solar Generation Prediction & Performance Assessment
                </div>
            </div>
        </div>
        <div class="status-pill">ML SYSTEM ONLINE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Site Configuration</div>
        <div class="section-caption">
            Select the solar campus and site you want to evaluate.
        </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    campus_options = sorted(sites["CampusKey"].dropna().unique().tolist())
    selected_campus = st.selectbox(
        "Campus",
        campus_options,
        format_func=lambda x: f"Campus {int(x)}",
    )

available_sites = (
    sites[sites["CampusKey"] == selected_campus]
    .sort_values("SiteKey")
    .copy()
)

with col2:
    site_options = available_sites["SiteKey"].astype(int).tolist()
    selected_site = st.selectbox(
        "Solar Site",
        site_options,
        format_func=lambda x: f"Site {int(x)}",
    )

selected_site_info = sites[
    (sites["CampusKey"] == selected_campus)
    & (sites["SiteKey"] == selected_site)
].iloc[0]

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Site Information</div>
        <div class="section-caption">
            Metadata retrieved directly from the SolarPulse MySQL database.
        </div>
    """,
    unsafe_allow_html=True,
)

def safe_display(value, decimals=None):
    if pd.isna(value):
        return "Not available"
    if decimals is not None:
        return f"{float(value):.{decimals}f}"
    return str(value)

st.markdown(
    f"""
    <div class="site-info-grid">
        <div class="site-info-item">
            <div class="site-info-label">Capacity</div>
            <div class="site-info-value">{safe_display(selected_site_info["kWp"], 2)}</div>
        </div>
        <div class="site-info-item">
            <div class="site-info-label">Panels</div>
            <div class="site-info-value">{safe_display(selected_site_info["Number_of_Panels"])}</div>
        </div>
        <div class="site-info-item">
            <div class="site-info-label">Panel</div>
            <div class="site-info-value">{safe_display(selected_site_info["Panel"])}</div>
        </div>
        <div class="site-info-item">
            <div class="site-info-label">Inverter</div>
            <div class="site-info-value">{safe_display(selected_site_info["Inverter"])}</div>
        </div>
        <div class="site-info-item">
            <div class="site-info-label">Latitude</div>
            <div class="site-info-value">{safe_display(selected_site_info["Latitude"], 4)}</div>
        </div>
        <div class="site-info-item">
            <div class="site-info-label">Longitude</div>
            <div class="site-info-value">{safe_display(selected_site_info["Longitude"], 4)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Prediction Time</div>
        <div class="section-caption">
            Enter the date and local time for the generation estimate.
        </div>
    """,
    unsafe_allow_html=True,
)

date_col, time_col = st.columns(2)

with date_col:
    prediction_date = st.date_input(
        "Date",
        value=date(2022, 4, 15),
    )

with time_col:
    prediction_time = st.time_input(
        "Time",
        value=time(12, 0),
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Weather Conditions</div>
        <div class="section-caption">
            Provide the environmental conditions. SolarPulse automatically
            converts these values into the same features used during training.
        </div>
    """,
    unsafe_allow_html=True,
)

row1a, row1b = st.columns(2)
with row1a:
    air_temperature = st.number_input(
        "Air Temperature (°C)",
        min_value=-20.0,
        max_value=60.0,
        value=25.0,
        step=0.1,
    )
with row1b:
    apparent_temperature = st.number_input(
        "Apparent Temperature (°C)",
        min_value=-25.0,
        max_value=65.0,
        value=25.0,
        step=0.1,
    )

row2a, row2b = st.columns(2)
with row2a:
    dew_point = st.number_input(
        "Dew Point Temperature (°C)",
        min_value=-30.0,
        max_value=45.0,
        value=15.0,
        step=0.1,
    )
with row2b:
    humidity = st.number_input(
        "Relative Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=60.0,
        step=1.0,
    )

row3a, row3b = st.columns(2)
with row3a:
    wind_speed = st.number_input(
        "Wind Speed",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
    )
with row3b:
    wind_direction = st.number_input(
        "Wind Direction (°)",
        min_value=0.0,
        max_value=360.0,
        value=180.0,
        step=1.0,
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Optional Performance Check</div>
        <div class="section-caption">
            Enable this when measured generation is available to compare
            actual output with model expectation.
        </div>
    """,
    unsafe_allow_html=True,
)

check_actual = st.checkbox("Compare against actual generation")
actual_generation = None

if check_actual:
    actual_generation = st.number_input(
        "Actual Energy Generation (kwh)",
        min_value=0.0,
        value=0.0,
        step=0.01,
    )

st.markdown("</div>", unsafe_allow_html=True)

predict_button = st.button(
    "☀️  PREDICT SOLAR GENERATION",
    type="primary",
    use_container_width=True,
)

if predict_button:
    try:
        prediction_features = create_prediction_features(
            selected_campus,
            selected_site,
            prediction_date,
            prediction_time,
            air_temperature,
            apparent_temperature,
            dew_point,
            humidity,
            wind_speed,
            wind_direction,
        )

        expected_features = list(
            getattr(
                model,
                "feature_names_in_",
                prediction_features.columns,
            )
        )

        missing_features = [
            feature
            for feature in expected_features
            if feature not in prediction_features.columns
        ]

        if missing_features:
            st.error(
                "The prediction feature set does not match the trained model."
            )
            st.write("Missing features:", missing_features)
            st.stop()

        prediction_features = prediction_features[expected_features]

        expected_generation = max(
            0.0,
            float(model.predict(prediction_features)[0]),
        )

        timestamp_label = pd.Timestamp.combine(
            prediction_date,
            prediction_time,
        ).strftime("%d %b %Y, %H:%M")

        st.markdown(
            f"""
            <div class="prediction-hero">
                <div class="prediction-label">Expected Solar Generation</div>
                <div class="prediction-value">{expected_generation:.2f} kwh</div>
                <div class="prediction-note">
                    Site {int(selected_site)} • Campus {int(selected_campus)}
                    • {timestamp_label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Model</div>
                    <div class="metric-value">Random Forest</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with metric2:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Test R²</div>
                    <div class="metric-value">84.2%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with metric3:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Test RMSE</div>
                    <div class="metric-value">4.88</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if check_actual and actual_generation is not None:
            deviation, performance_ratio, status = performance_assessment(
                actual_generation,
                expected_generation,
                PERFORMANCE_FLOOR,
                WARNING_THRESHOLD,
                CRITICAL_THRESHOLD,
            )

            st.markdown(
                """
                <div class="section-card">
                    <div class="section-title">Performance Assessment</div>
                    <div class="section-caption">
                        Actual output compared with model-estimated expected generation.
                    </div>
                """,
                unsafe_allow_html=True,
            )

            a, b, c = st.columns(3)

            with a:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Actual Generation</div>
                        <div class="metric-value">{actual_generation:.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with b:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Expected Generation</div>
                        <div class="metric-value">{expected_generation:.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c:
                deviation_text = (
                    "N/A" if deviation is None else f"{deviation:.1f}%"
                )
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Performance Deviation</div>
                        <div class="metric-value">{deviation_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if status == "Normal":
                st.markdown(
                    '<div class="status-normal">🟢 NORMAL — Actual generation is within the expected performance range.</div>',
                    unsafe_allow_html=True,
                )
            elif status == "Warning":
                st.markdown(
                    '<div class="status-warning">🟠 WARNING — Actual generation is materially below model expectation and may require review.</div>',
                    unsafe_allow_html=True,
                )
            elif status == "Critical":
                st.markdown(
                    '<div class="status-critical">🔴 CRITICAL — Actual generation is substantially below model expectation and should be investigated.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="status-na">⚪ NOT APPLICABLE — Expected generation is too low for a reliable percentage-based assessment.</div>',
                    unsafe_allow_html=True,
                )

            if performance_ratio is not None:
                st.markdown(
                    f"""
                    <div style="margin-top:.8rem;color:#64748b;font-size:.86rem;">
                        Performance ratio:
                        <strong>{performance_ratio * 100:.1f}%</strong>
                        of expected generation.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("View model inputs and detection rules"):
            st.write("**Model input features**")
            st.code(
                "\n".join(expected_features),
                language="text",
            )
            st.write("**Detection configuration**")
            st.json(
                {
                    "Performance floor": PERFORMANCE_FLOOR,
                    "Warning threshold (%)": WARNING_THRESHOLD,
                    "Critical threshold (%)": CRITICAL_THRESHOLD,
                }
            )

    except Exception as exc:
        st.error("Prediction failed. Please check the inputs and model files.")
        st.exception(exc)

st.markdown(
    """
    <div class="footer">
        SolarPulse • SQL + Pandas + Machine Learning + Streamlit
        <br>
        Expected generation is estimated using the trained Random Forest model.
    </div>
    """,
    unsafe_allow_html=True,
)
