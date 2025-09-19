import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Railway Traffic Optimizer", layout="wide")
st.title("OptiPravah - Optimized Train Tracking & Scheduling Platform")

# --- Step 1: Define Train Data ---
st.subheader("📋 Original Train Schedule")

train_data = [
    {"Train ID": "A", "Type": "Superfast", "Priority": 3, "Arrival": "10:00", "Halt": 5, "Platform": 1},
    {"Train ID": "B", "Type": "Passenger", "Priority": 2, "Arrival": "10:10", "Halt": 15, "Platform": 1},
    {"Train ID": "C", "Type": "Freight", "Priority": 1, "Arrival": "10:05", "Halt": 20, "Platform": 2},
    {"Train ID": "D", "Type": "Local", "Priority": 2, "Arrival": "10:15", "Halt": 10, "Platform": 2}
]

df = pd.DataFrame(train_data)

# --- Step 2: Simulate Delay ---
st.subheader("⚠️ Simulating Delay or Disruption")

delayed_train = st.selectbox("Select train to delay", options=["None"] + df["Train ID"].tolist())
delay_minutes = st.slider("Delay duration (minutes)", 0, 30, 10) if delayed_train != "None" else 0

for i in range(len(df)):
    if df.loc[i, "Train ID"] == delayed_train:
        original_arrival = datetime.strptime(df.loc[i, "Arrival"], "%H:%M")
        new_arrival = original_arrival + timedelta(minutes=delay_minutes)
        df.loc[i, "Arrival"] = new_arrival.strftime("%H:%M")
        df.loc[i, "Delay"] = delay_minutes
    else:
        df.loc[i, "Delay"] = 0

st.dataframe(df)

# --- Step 3: Decision Logic ---
st.subheader("Optimized Platform Assignment & Status")

df["Arrival_dt"] = pd.to_datetime(df["Arrival"], format="%H:%M")
df["Departure_dt"] = df["Arrival_dt"] + pd.to_timedelta(df["Halt"], unit="m")

# Sort by priority first, then arrival time
df_sorted = df.sort_values(by=["Priority", "Arrival_dt"], ascending=[False, True]).reset_index(drop=True)

platform_status = {1: [], 2: []}
decision = []

for i, row in df_sorted.iterrows():
    plat = row["Platform"]
    arrival = row["Arrival_dt"]
    departure = row["Departure_dt"]
    halt = row["Halt"]
    priority = row["Priority"]
    delay = row["Delay"]

    can_arrive = True
    override = False

    # Check for conflicts
    for other in platform_status[plat]:
        other_arrival, other_departure, other_priority = other

        # Conflict detected
        if arrival < other_departure and departure > other_arrival:
            can_arrive = False

            # Delay-aware override logic
            delay_gap = (other_departure - arrival).seconds // 60
            if priority < other_priority and halt <= delay_gap:
                override = True
            break

    if can_arrive or override:
        platform_status[plat].append((arrival, departure, priority))
        decision.append({
            "Train ID": row["Train ID"],
            "Type": row["Type"],
            "Priority": priority,
            "Arrival": row["Arrival"],
            "Halt": halt,
            "Delay": delay,
            "Platform": plat,
            "Decision": "✅ Proceed",
            "Status": "🟢 Can Arrive at Platform"
        })
    else:
        decision.append({
            "Train ID": row["Train ID"],
            "Type": row["Type"],
            "Priority": priority,
            "Arrival": row["Arrival"],
            "Halt": halt,
            "Delay": delay,
            "Platform": plat,
            "Decision": "⏳ Wait",
            "Status": "🔴 Cannot Arrive – Platform Occupied"
        })

df_final = pd.DataFrame(decision)
st.dataframe(df_final)

# --- Step 4: KPIs ---
st.subheader("📈 KPIs")

avg_delay = df_final["Delay"].mean()
total_trains = len(df_final)
proceeding = df_final[df_final["Decision"] == "✅ Proceed"].shape[0]
waiting = df_final[df_final["Decision"] == "⏳ Wait"].shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🚉 Total Trains", total_trains)
col2.metric("✅ Proceeding", proceeding)
col3.metric("⏳ Waiting", waiting)
col4.metric("📊 Avg Delay", f"{avg_delay:.1f} min")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 14px; color: gray;'>"
    "© Original Work by <b>Saidhiraj</b> – Conceptualized, Designed, and Simulated for SIH 2025."
    "</div>",
    unsafe_allow_html=True
)

