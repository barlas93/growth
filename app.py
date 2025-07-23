import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Child Growth Chart Projection Tool")

sex = st.selectbox("Sex", options=["Male", "Female"])
current_age = st.slider("Current Age (years)", min_value=0, max_value=18, value=10)
current_height = st.number_input("Current Height (cm)", min_value=30.0, max_value=200.0, value=140.0)
target_age = st.slider("Target Age (years)", min_value=0, max_value=18, value=15)

filename = "growthmale.csv" if sex == "Male" else "growthfemale.csv"
data = pd.read_csv(filename)

data = data.sort_values(by="Age")

grouped = data.groupby("Age")["Height"]
percentiles = grouped.quantile([0.05, 0.5, 0.95]).unstack()

ages = percentiles.index
p5 = percentiles[0.05]
p50 = percentiles[0.5]
p95 = percentiles[0.95]

# Determine current percentile
def estimate_percentile(age, height):
    if age not in ages:
        return None
    heights_at_age = grouped.get_group(age)
    return round((heights_at_age < height).mean(), 2)

percentile_rank = estimate_percentile(current_age, current_height)

def predict_height(target_age, percentile):
    if target_age not in ages:
        return None
    heights_at_age = grouped.get_group(target_age)
    return round(np.percentile(heights_at_age, percentile * 100), 1)

predicted_height = predict_height(target_age, percentile_rank)

if predicted_height is not None:
    st.markdown(f"### Estimated Height at Age {target_age}: **{predicted_height} cm**")
else:
    st.warning("Target age is outside the data range.")

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
