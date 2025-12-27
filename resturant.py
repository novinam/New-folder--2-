import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RABT IWAN Ops Dashboard", layout="wide")

st.title("🍕 Restaurant Operations Dashboard")

# ---------------- SETTINGS ----------------
st.sidebar.header("⚙️ Settings")

safety_normal = st.sidebar.number_input("Safety Factor (Normal Day)", value=1.1, step=0.1)
safety_weekend = st.sidebar.number_input("Safety Factor (Weekend)", value=1.3, step=0.1)
min_days = st.sidebar.number_input("Min Stock (Days)", value=1)
max_days = st.sidebar.number_input("Max Stock (Days)", value=3)
waste_limit = st.sidebar.number_input("Waste Limit (%)", value=5) / 100

# ---------------- BOM ----------------
st.header("📦 Menu BOM (Per Item Usage)")

bom = pd.DataFrame({
    "Ingredient": ["Dough", "Cheese", "Sauce"],
    "Usage_per_Item_g": [250, 120, 80]
})

st.dataframe(bom, use_container_width=True)

# ---------------- SALES INPUT ----------------
st.header("🧾 Daily Sales Input")

col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("Date", value=datetime.today())
with col2:
    qty_sold = st.number_input("Pizzas Sold Today", min_value=0, value=40)
with col3:
    day_type = st.selectbox("Day Type", ["Normal", "Weekend"])

factor = safety_normal if day_type == "Normal" else safety_weekend

# ---------------- CALCULATIONS ----------------
daily_usage = bom.copy()
daily_usage["Daily_Usage_g"] = daily_usage["Usage_per_Item_g"] * qty_sold * factor
daily_usage["Min_Stock_g"] = daily_usage["Daily_Usage_g"] * min_days
daily_usage["Max_Stock_g"] = daily_usage["Daily_Usage_g"] * max_days

st.subheader("📊 Calculated Daily Usage")
st.dataframe(daily_usage, use_container_width=True)

# ---------------- INVENTORY ----------------
st.header("🏬 Current Inventory")

inventory = {}
for ing in daily_usage["Ingredient"]:
    inventory[ing] = st.number_input(f"{ing} Stock (g)", min_value=0, value=5000)

daily_usage["Current_Stock_g"] = daily_usage["Ingredient"].map(inventory)
daily_usage["Need_Delivery"] = daily_usage["Current_Stock_g"] <= daily_usage["Min_Stock_g"]

st.subheader("🚚 Delivery Status")
st.dataframe(daily_usage[[
    "Ingredient",
    "Current_Stock_g",
    "Min_Stock_g",
    "Max_Stock_g",
    "Need_Delivery"
]], use_container_width=True)

# ---------------- WASTE ----------------
st.header("♻️ Waste Logging")

waste_data = {}
for ing in daily_usage["Ingredient"]:
    waste_data[ing] = st.number_input(f"Waste {ing} (g)", min_value=0, value=0)

daily_usage["Waste_g"] = daily_usage["Ingredient"].map(waste_data)

total_usage = daily_usage["Daily_Usage_g"].sum()
total_waste = daily_usage["Waste_g"].sum()

waste_percent = (total_waste / total_usage) if total_usage > 0 else 0

st.subheader("📉 Waste KPI")

col1, col2, col3 = st.columns(3)
col1.metric("Total Usage (g)", int(total_usage))
col2.metric("Total Waste (g)", int(total_waste))
col3.metric("Waste %", f"{waste_percent:.1%}",
            delta="OK" if waste_percent <= waste_limit else "HIGH")

if waste_percent > waste_limit:
    st.error("🚨 Waste is above acceptable limit!")
else:
    st.success("✅ Waste level is under control")

st.caption("Ops Logic: Average Sales × Safety Factor → Min/Max → Scheduled Delivery")
