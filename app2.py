import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# --- Input Data ---
data = [
    {"Train ID": "T1", "Type": "Passenger", "Priority": 3, "Arrival": "10:00", "Departure": "10:10"},
    {"Train ID": "T2", "Type": "Express", "Priority": 2, "Arrival": "10:05", "Departure": "10:15"},
    {"Train ID": "T3", "Type": "Freight", "Priority": 1, "Arrival": "10:07", "Departure": "10:20"}
]
df = pd.DataFrame(data)

st.title("🚆 Smart Train Scheduler (Prototype)")

# Show input table
st.subheader("Train Schedule Input")
st.dataframe(df)

# Add disruption
st.subheader("Disruption Simulator")
delayed_train = st.selectbox("Select train to delay", df["Train ID"])
delay_minutes = st.slider("Delay (minutes)", 0, 30, 5)

# Apply delay
if delayed_train:
    idx = df[df["Train ID"] == delayed_train].index[0]
    arr_time = datetime.strptime(df.loc[idx, "Arrival"], "%H:%M")
    dep_time = datetime.strptime(df.loc[idx, "Departure"], "%H:%M")
    df.loc[idx, "Arrival"] = (arr_time + timedelta(minutes=delay_minutes)).strftime("%H:%M")
    df.loc[idx, "Departure"] = (dep_time + timedelta(minutes=delay_minutes)).strftime("%H:%M")

# Sort by priority + arrival time
df_sorted = df.sort_values(by=["Priority", "Arrival"], ascending=[False, True])

st.subheader("📋 Optimized Train Order")
st.dataframe(df_sorted)

# KPI
avg_delay = delay_minutes if delayed_train else 0
st.metric("Average Delay (mins)", avg_delay)
st.metric("Total Trains Processed", len(df))

# --- Visualization ---
st.subheader("🚦 Track Visualization")

track_length = 20  # fixed track length for visualization

# Define train colors
def train_color(train_type):
    if train_type == "Express":
        return "green"
    elif train_type == "Passenger":
        return "blue"
    else:
        return "orange"

# Animation container
placeholder = st.empty()

animate = st.checkbox("Enable Animation", value=True)

if animate:
    for step in range(track_length):
        with placeholder.container():
            for _, row in df_sorted.iterrows():
                color = train_color(row["Type"])
                position = "⬛" * step + f"<span style='background-color:{color};padding:4px 10px;border-radius:5px;color:white'>{row['Train ID']}</span>"
                st.markdown(position, unsafe_allow_html=True)
            time.sleep(0.3)  # control animation speed
else:
    # Static blocks
    for _, row in df_sorted.iterrows():
        color = train_color(row["Type"])
        st.markdown(
            f"<div style='padding:10px;background-color:{color};margin:5px;border-radius:5px;color:white'>{row['Train ID']} ({row['Type']})</div>",
            unsafe_allow_html=True,
        )
