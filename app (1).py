
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

st.set_page_config(
    page_title="AI Predictive Maintenance",
    page_icon="⚙️",
    layout="wide"
)

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------
st.title("AI-Driven Predictive Maintenance")
st.subheader("Industrial Machine Monitoring Using LoRa")
st.caption(
    "STM32 | LoRa Communication | AI Fault Detection | "
    "Maintenance Analytics"
)

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------
@st.cache_resource
def load_model():
    model_path = "motor_fault_model.pkl"

    if os.path.exists(model_path):
        return joblib.load(model_path)

    return None

model = load_model()

if model is None:
    st.error(
        "AI model file not found. Upload motor_fault_model.pkl "
        "to the same GitHub folder as app.py."
    )
    st.stop()

# --------------------------------------------------
# SIDEBAR INPUTS
# --------------------------------------------------
st.sidebar.header("Motor Sensor Readings")
st.sidebar.write("Enter readings received from your sensors.")

temperature = st.sidebar.number_input(
    "Temperature (°C)",
    min_value=0.0,
    max_value=200.0,
    value=82.0,
    step=1.0
)

vibration = st.sidebar.number_input(
    "Vibration (g)",
    min_value=0.0,
    max_value=10.0,
    value=1.05,
    step=0.05
)

current = st.sidebar.number_input(
    "Motor Current (A)",
    min_value=0.0,
    max_value=100.0,
    value=9.5,
    step=0.5
)

analyse = st.sidebar.button(
    "Analyse Motor",
    type="primary",
    use_container_width=True
)

# --------------------------------------------------
# ANALYSE SENSOR DATA
# --------------------------------------------------
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = {
        "temperature": temperature,
        "vibration": vibration,
        "current": current
    }

if analyse:
    st.session_state.sensor_data = {
        "temperature": temperature,
        "vibration": vibration,
        "current": current
    }

data = st.session_state.sensor_data

temperature = data["temperature"]
vibration = data["vibration"]
current = data["current"]

X = pd.DataFrame([{
    "temperature_C": temperature,
    "vibration_g": vibration,
    "current_A": current
}])

fault = model.predict(X)[0]
probabilities = model.predict_proba(X)[0]
confidence = float(np.max(probabilities)) * 100

# --------------------------------------------------
# MAINTENANCE PRIORITY
# Example thresholds; calibrate for the actual motor.
# --------------------------------------------------
if (
    temperature >= 95
    or vibration >= 1.5
    or current >= 13
):
    risk = "HIGH"
    action = "Urgent inspection recommended"

elif (
    temperature >= 80
    or vibration >= 0.9
    or current >= 10
):
    risk = "MODERATE"
    action = "Schedule maintenance inspection"

else:
    risk = "LOW"
    action = "Continue condition monitoring"

# --------------------------------------------------
# COMPONENT AND REPAIR ESTIMATES
# Indicative planning ranges only.
# --------------------------------------------------
repair_guide = {
    "Bearing / Vibration Fault": {
        "component": "Bearing / rotating assembly",
        "repair_time": "2–6 hours",
        "recommendation": (
            "Inspect bearing wear, lubrication and vibration."
        )
    },
    "Overheating": {
        "component": "Cooling system / winding",
        "repair_time": "1–4 hours initially",
        "recommendation": (
            "Inspect cooling, ventilation, load and winding temperature."
        )
    },
    "Electrical Overload": {
        "component": "Electrical circuit / motor load",
        "repair_time": "1–3 hours initially",
        "recommendation": (
            "Check phase currents, supply, load and connections."
        )
    },
    "Misalignment / Imbalance": {
        "component": "Shaft / coupling / rotor",
        "repair_time": "2–5 hours",
        "recommendation": (
            "Inspect shaft alignment, coupling and rotor balance."
        )
    },
    "Normal": {
        "component": "No fault indicated by the model",
        "repair_time": "Not applicable",
        "recommendation": (
            "Continue routine monitoring and scheduled inspection."
        )
    }
}

guide = repair_guide.get(
    fault,
    {
        "component": "Requires technician inspection",
        "repair_time": "To be determined",
        "recommendation": (
            "Verify sensor readings and inspect the machine."
        )
    }
)

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------
st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Temperature", f"{temperature:.1f} °C")
col2.metric("Vibration", f"{vibration:.2f} g")
col3.metric("Current", f"{current:.2f} A")
col4.metric("Maintenance Risk", risk)

if risk == "HIGH":
    st.error("HIGH PRIORITY: " + action)
elif risk == "MODERATE":
    st.warning("MODERATE PRIORITY: " + action)
else:
    st.success("LOW PRIORITY: " + action)

# --------------------------------------------------
# AI DIAGNOSIS AND MAINTENANCE PLAN
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("AI Fault Diagnosis")
    st.write("**Predicted condition:**", fault)
    st.write("**Suspected component:**", guide["component"])
    st.write("**Model confidence:**", f"{confidence:.1f}%")

    st.caption(
        "Model confidence is not the probability of a future failure."
    )

with right:
    st.subheader("Maintenance Recommendation")
    st.write("**Priority:**", risk)
    st.write("**Recommended action:**", action)
    st.write("**Indicative repair time:**", guide["repair_time"])
    st.write("**Inspection:**", guide["recommendation"])

st.info(
    "Repair durations and risk thresholds are illustrative. "
    "Validate them using motor specifications and real maintenance records."
)

# --------------------------------------------------
# SENSOR GRAPHS
# --------------------------------------------------
st.divider()
st.subheader("Motor Sensor Analysis")

fig, axes = plt.subplots(1, 3, figsize=(13, 4))

sensor_names = ["Temperature", "Vibration", "Current"]
sensor_values = [temperature, vibration, current]
sensor_units = ["°C", "g", "A"]

for ax, name, value, unit in zip(
    axes, sensor_names, sensor_values, sensor_units
):
    ax.bar([name], [value])
    ax.set_title(name)
    ax.set_ylabel(unit)
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# --------------------------------------------------
# MODEL FAULT CATEGORY SCORES
# --------------------------------------------------
st.subheader("AI Fault Category Scores")

score_df = pd.DataFrame({
    "Fault Category": model.classes_,
    "Model Score (%)": probabilities * 100
}).sort_values("Model Score (%)", ascending=False)

st.bar_chart(
    score_df.set_index("Fault Category")
)

# --------------------------------------------------
# DOWNLOAD MAINTENANCE REPORT
# --------------------------------------------------
st.divider()
st.subheader("Maintenance Report")

report = pd.DataFrame([{
    "Temperature_C": temperature,
    "Vibration_g": vibration,
    "Current_A": current,
    "Predicted_Fault": fault,
    "Maintenance_Risk": risk,
    "Suspected_Component": guide["component"],
    "Indicative_Repair_Time": guide["repair_time"],
    "Recommended_Action": action,
    "Model_Confidence_Percent": round(confidence, 2)
}])

st.dataframe(report, use_container_width=True)

st.download_button(
    label="Download Maintenance Report (CSV)",
    data=report.to_csv(index=False).encode("utf-8"),
    file_name="maintenance_report.csv",
    mime="text/csv"
)

st.caption(
    "Prototype dashboard: sensor inputs are manual until a live "
    "LoRa receiver/API is connected. Model scores and fault labels "
    "require validation against real machine data."
)
