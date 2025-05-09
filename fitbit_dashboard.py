import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# --- Load access token from Streamlit secrets ---
access_token = st.secrets["access_token"]
# Optional: you can also access these if needed later
# refresh_token = st.secrets["refresh_token"]
# expires_at = st.secrets["expires_at"]

headers = {
    "Authorization": f"Bearer {access_token}"
}

# --- Define date range ---
num_days = 7
end_date = datetime.today()
dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in reversed(range(num_days))]

# --- Initialize data lists ---
calories_by_date = []
steps_by_date = []
sleep_by_date = []

# --- Pull Fitbit data per day ---
for date_str in dates:
    # --- Calories ---
    url = f"https://api.fitbit.com/1/user/-/foods/log/date/{date_str}.json"
    res = requests.get(url, headers=headers)
    calories = res.json().get("summary", {}).get("calories", 0) if res.status_code == 200 else 0
    calories_by_date.append(calories)

    # --- Sleep ---
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date_str}.json"
    res = requests.get(url, headers=headers)
    minutes_asleep = res.json().get("summary", {}).get("totalMinutesAsleep", 0) if res.status_code == 200 else 0
    sleep_by_date.append(minutes_asleep)

    # --- Steps ---
    url = f"https://api.fitbit.com/1/user/-/activities/date/{date_str}.json"
    res = requests.get(url, headers=headers)
    steps = res.json().get("summary", {}).get("steps", 0) if res.status_code == 200 else 0
    steps_by_date.append(steps)

# --- Pull goal data for the most recent day ---
goal_url = f"https://api.fitbit.com/1/user/-/activities/date/{dates[-1]}.json"
res = requests.get(goal_url, headers=headers)
goal_data = res.json().get("goals", {}) if res.status_code == 200 else {}
daily_goal_steps = goal_data.get("steps", 0)
daily_goal_calories = goal_data.get("caloriesOut", 0)

# --- Streamlit UI ---
st.title("📊 Fitbit 7-Day Health Dashboard")
st.subheader(f"Showing data for: {dates[0]} to {dates[-1]}")

# --- DataFrame ---
df = pd.DataFrame({
    "Date": dates,
    "Calories": calories_by_date,
    "Steps": steps_by_date,
    "Sleep (min)": sleep_by_date
}).set_index("Date")

# --- Plot all metrics ---
st.line_chart(df)

# --- Show daily goals ---
st.markdown("### 🎯 Daily Goals")
st.markdown(f"- **Step Goal:** {daily_goal_steps}")
st.markdown(f"- **Calorie Burn Goal:** {daily_goal_calories}")

# --- Show raw data ---
st.markdown("### 🔍 Raw Data")
st.dataframe(df)
