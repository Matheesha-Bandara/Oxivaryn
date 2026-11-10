import sys
from pathlib import Path
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

# Locate project directories

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from pdf_report import generate_pdf_report
from measurement_analysis import calculate_sensor_metrics

# Page Configuration 

st.set_page_config(
    page_title="Oxivaryn",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Oxivaryn")

st.subheader(
    "Oxygen Sensor Performance Assessment System"
)

st.info(
    "Educational research prototype created by Matheesha Bandara "

)

# Data Source

st.markdown("### 1. Measurement Data")

data_source = st.radio(
    "Select Data Source",
    ["Simulated Data", "Upload CSV"],
    horizontal=True
)

if data_source == "Simulated Data":

    original_df = pd.read_csv(
        ROOT / "data" / "oxygen_sensor_data.csv"
    )

    sensor = st.selectbox(
        "Select Simulated Sensor Condition",
        ["Healthy", "Drifting", "Degraded"]
    )

    df = original_df[
        ["Time", "Reference_Oxygen", sensor]
    ].copy()

    df.rename(
        columns={sensor: "Sensor_Reading"},
        inplace=True
    )

else:

    uploaded_file = st.file_uploader(
        "Upload Sensor Measurement CSV",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "Upload a CSV containing Time, "
            "Reference_Oxygen and Sensor_Reading."
        )
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Unable to read the CSV file.")
        st.stop()

# Data Validation

required_columns = [
    "Time",
    "Reference_Oxygen",
    "Sensor_Reading"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(
        "Missing columns: " + ", ".join(missing)
    )
    st.stop()

df = df[required_columns].copy()

for col in required_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

if df.isna().any().any():
    st.error(
        "Dataset contains missing or invalid values."
    )
    st.stop()

if not np.isfinite(df.to_numpy()).all():
    st.error("Dataset contains non-finite values.")
    st.stop()

if len(df) < 3:
    st.error(
        "At least three measurements are required."
    )
    st.stop()

if (
    not df["Time"].is_monotonic_increasing
    or df["Time"].duplicated().any()
):
    st.error(
        "Time values must be strictly increasing."
    )
    st.stop()

for col in ["Reference_Oxygen", "Sensor_Reading"]:
    if ((df[col] < 0) | (df[col] > 100)).any():
        st.error(
            f"{col} must contain values between 0 and 100."
        )
        st.stop()

# Test Information

st.markdown("### 2. Test Information")

col1, col2 = st.columns(2)

with col1:

    sensor_model = st.text_input(
        "Sensor Model",
        value="Simulated Electrochemical O2 Sensor"
        if data_source == "Simulated Data"
        else ""
    )

    sensor_id = st.text_input(
        "Sensor Identification Number",
        value="SIM-001"
        if data_source == "Simulated Data"
        else ""
    )

with col2:

    test_date = st.date_input(
        "Test Date",
        value=date.today()
    )

    technician = st.text_input(
        "Test Operator / Researcher",
        value=""
    )

# Time Settings

st.markdown("### 3. Measurement Time Settings")

if data_source == "Simulated Data":

    time_unit = "measurement"

    st.caption(
        "Simulation time represents measurement indices, "
        "not actual elapsed time."
    )

else:

    time_unit = st.selectbox(
        "Unit of the Time Column",
        ["seconds", "minutes", "hours", "measurement"]
    )

st.caption(
    "The time unit must match the uploaded dataset. "
    "Changing the selection does not convert the data."
)

# Reference Information

st.markdown("### 4. Reference Oxygen Information")

if data_source == "Simulated Data":

    reference_source = "Simulated 40% Oxygen Reference"

    st.write(
        "**Reference Source:**",
        reference_source
    )

else:

    reference_source = st.text_input(
        "Reference Measurement Source",
        placeholder="e.g. calibrated oxygen analyzer"
    )

    st.caption(
        "Specify the instrument or method used to "
        "obtain the reference oxygen measurements."
    )

reference_mean = df["Reference_Oxygen"].mean()

st.write(
    f"**Mean Reference Oxygen:** {reference_mean:.2f}%"
)

# Performance Calculations

time = df["Time"].to_numpy()
reference = df["Reference_Oxygen"].to_numpy()
readings = df["Sensor_Reading"].to_numpy()

metrics = calculate_sensor_metrics(
    time=df["Time"],
    reference=df["Reference_Oxygen"],
    readings=df["Sensor_Reading"]
)

mae = metrics["mae"]
bias = metrics["bias"]
max_error = metrics["max_error"]
slope = metrics["slope"]
stability = metrics["stability"]

error = df["Sensor_Reading"] - df["Reference_Oxygen"]

# Performance Metrics

st.markdown("### 5. Sensor Performance Metrics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Mean Absolute Error",
    f"{mae:.3f} pp"
)

col2.metric(
    "Stability (Residual SD)",
    f"{stability:.3f} pp"
)

col3.metric(
    "Drift Slope",
    f"{slope:.4f} pp/{time_unit}"
)

col4, col5 = st.columns(2)

col4.metric(
    "Mean Signed Error (Bias)",
    f"{bias:.3f} pp"
)

col5.metric(
    "Maximum Absolute Error",
    f"{max_error:.3f} pp"
)

st.caption(
    "pp = percentage points. For example, "
    "40% reference oxygen versus 38% measured oxygen "
    "corresponds to an error of -2 pp."
)

# Performance Assessment 

st.markdown("### 6. Performance Assessment")

if data_source == "Simulated Data":

    # Illustrative thresholds for simulated data only

    if (
        mae <= 0.5
        and abs(slope) <= 0.01
        and stability <= 0.3
    ):

        status = "Stable Measurement Pattern"

        explanation = (
            "The simulated sensor demonstrates low "
            "measurement error, minimal drift and "
            "low random variability."
        )

        st.success(status)

    elif (
        mae <= 3.0
        and abs(slope) <= 0.06
        and stability <= 0.5
    ):

        status = "Possible Performance Deterioration"

        explanation = (
            "The simulated sensor demonstrates "
            "increased measurement error or drift."
        )

        st.warning(status)

    else:

        status = "Significant Measurement Deviation"

        explanation = (
            "The simulated sensor demonstrates "
            "substantial measurement error, drift "
            "or random variability."
        )

        st.error(status)

else:

    status = "Descriptive Analysis Only"

    explanation = (
        "Performance statistics have been calculated "
        "from the uploaded dataset. No validated "
        "manufacturer-specific acceptance criteria "
        "have been applied."
    )

    st.info(status)

st.write(explanation)

# Measurement Trend Graph 

st.markdown("### 7. Oxygen Measurement Trends")

chart_df = df.set_index("Time")[
    ["Reference_Oxygen", "Sensor_Reading"]
].rename(columns={
    "Reference_Oxygen": "Reference Oxygen (%)",
    "Sensor_Reading": "Sensor Reading (%)"
})

st.line_chart(chart_df)

st.caption(
    f"Horizontal axis: {time_unit}. "
    "Vertical axis: oxygen concentration (%)."
)

# Measurement Error Graph 

st.markdown("### 8. Measurement Error Analysis")

error_df = pd.DataFrame({
    "Time": time,
    "Measurement Error (pp)": error
}).set_index("Time")

st.line_chart(error_df)

st.caption(
    "Measurement error = Sensor Reading - Reference. "
    "Negative values indicate under-reading."
)

# Measurement Data 

st.markdown("### 9. Measurement Data")

display_df = df.copy()

display_df["Error_pp"] = error

st.dataframe(
    display_df,
    use_container_width=True
)

# PDF Report

st.markdown("### 10. Download Performance Report")


pdf_bytes = generate_pdf_report(
    df=df,
    data_source=data_source,
    mae=mae,
    stability=stability,
    slope=slope,
    status=status,
    explanation=explanation,
    time_unit=time_unit,
    sensor_model=sensor_model,
    sensor_id=sensor_id,
    technician=technician,
    test_date=test_date,
    reference_source=reference_source,
    bias=bias,
    max_error=max_error
)


st.download_button(
    label="📄 Download PDF Performance Report",
    data=pdf_bytes,
    file_name="Oxivaryn_Performance_Report.pdf",
    mime="application/pdf"
)


