import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Child Growth Chart Projection Tool")

# --- Conversion Functions ---
def cm_to_feet_inches(cm):
    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = round(total_inches % 12, 1)
    return feet, inches

def feet_inches_to_cm(feet, inches):
    return round((feet * 12 + inches) * 2.54, 1)

# --- User Inputs ---
sex = st.selectbox("Sex", options=["Male", "Female"])
current_age = st.slider("Current Age (years)", min_value=0, max_value=18, value=10)
target_age = st.slider("Target Age (years)", min_value=0, max_value=18, value=15)

# --- Height Input Method ---
height_unit = st.selectbox("Select Height Unit", options=["Centimeters (cm)", "Feet/Inches (ft/in)"])

if height_unit == "Centimeters (cm)":
    current_height = st.number_input("Current Height (cm)", min_value=30.0, max_value=200.0, value=140.0)
else:
    feet = st.number_input("Feet", min_value=1, max_value=8, value=4)
    inches = st.number_input("Inches", min_value=0.0, max_value=11.9, value=7.0, step=0.1)
    current_height = feet_inches_to_cm(feet, inches)
    st.markdown(f"Converted Height: **{current_height} cm**")

# --- Load Data ---
filename = "growthmale.csv" if sex == "Male" else "growthfemale.csv"
data = pd.read_csv(filename)
data = data.sort_values(by="Age")

grouped = data.groupby("Age")["Height"]
percentiles = grouped.quantile([0.05, 0.5, 0.95]).unstack()

ages = percentiles.index
p5 = percentiles[0.05]
p50 = percentiles[0.5]
p95 = percentiles[0.95]

# --- Estimate Current Percentile ---
def estimate_percentile(age, height):
    if age not in ages:
        return None
    heights_at_age = grouped.get_group(age)
    return round((heights_at_age < height).mean(), 2)

percentile_rank = estimate_percentile(current_age, current_height)

# --- Predict Future Height ---
def predict_height(target_age, percentile):
    if target_age not in ages:
        return None
    heights_at_age = grouped.get_group(target_age)
    return round(np.percentile(heights_at_age, percentile * 100), 1)

predicted_height = predict_height(target_age, percentile_rank)

# --- Display Result ---
if predicted_height is not None:
    st.markdown(f"### Estimated Height at Age {target_age}: **{predicted_height} cm**")
    feet_pred, inch_pred = cm_to_feet_inches(predicted_height)
    st.markdown(f"Which is approximately: **{feet_pred} ft {inch_pred} in**")
else:
    st.warning("Target age is outside the data range.")

# --- Plot Chart ---
fig, ax = plt.subplots()
ax.plot(ages, p5, label="5th Percentile", linestyle="--")
ax.plot(ages, p50, label="50th Percentile (Median)", linestyle="-")
ax.plot(ages, p95, label="95th Percentile", linestyle="--")
ax.scatter(current_age, current_height, color='blue', label="Current Height", zorder=5)
if predicted_height:
    ax.scatter(target_age, predicted_height, color='red', label="Predicted Height", zorder=5)

ax.set_title("Growth Chart")
ax.set_xlabel("Age (years)")
ax.set_ylabel("Height (cm)")
ax.legend()
ax.grid(True)

st.pyplot(fig)
