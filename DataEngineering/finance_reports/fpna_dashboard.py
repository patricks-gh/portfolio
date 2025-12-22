import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import base64

# Path to your image
revenue_icon = Path("icons/revenue.png")

# Encode as base64
with open(revenue_icon, "rb") as f:
    data = f.read()
img_base64 = base64.b64encode(data).decode()

# ---- Page config ----
st.set_page_config(page_title="FP&A Dashboard", layout="wide")
st.title("FP&A Dashboard – Income Statement")

# ---- Load Excel ----
df = pd.read_excel("income_statement_dashboard_data.xlsx", sheet_name="actuals", header=None)
targets_df = pd.read_excel("income_statement_dashboard_data.xlsx", sheet_name="targets", header=None)

# ---- Past 4 Year Average Actuals ----
total_revenue = df.iloc[4, 1]
total_cogs = df.iloc[9, 1]
gross_profit = df.iloc[10, 1]
gross_profit_margin = df.iloc[11, 1]

# ---- 2025–2022 Actuals vs Targets ----
years = ["2025", "2024", "2023", "2022"]
year_cols = [2, 3, 4, 5]  # Adjust based on your Excel
revenues = [df.iloc[4, col] for col in year_cols]
target_cols = [2, 3, 4, 5]
targets = [targets_df.iloc[4, col] for col in target_cols]

def format_million_with_arrow(value, target):
    """Return $M with arrow and color depending on target"""
    value_m = value / 1_000_000
    if value >= target:
        arrow = "↑"
        color = "#2E8B57"  # green
    else:
        arrow = "↓"
        color = "#FF4500"  # red
    return f"${value_m:.2f}M {arrow}", color


def delta_bar(actual, target, max_pct=50):
    """
    Visual delta bar vs target
    max_pct caps the bar at ±max_pct%
    """
    pct = (actual - target) / target * 100
    capped_pct = max(-max_pct, min(max_pct, pct))

    bar_width = abs(capped_pct) / max_pct * 50  # % of half-bar
    color = "#2E8B57" if pct >= 0 else "#FF4500"
    align = "right" if pct >= 0 else "left"

    return f"""
    <div style="width:100%; height:10px; background:#eee; position:relative; border-radius:5px;">
        <div style="
            position:absolute;
            height:100%;
            width:{bar_width}%;
            background:{color};
            {align}:50%;
            border-radius:5px;
        "></div>
    </div>
    """

# ---- Headers outside containers ----
col1_header, col2_header = st.columns([2, 1])
with col1_header:
    st.markdown(
        f'''
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
        <div style="font-family: 'Lato', sans-serif; font-size:30px; color:#4682B4; font-weight:900; display:flex; align-items:center; padding-bottom: 10px">
            <img src="data:image/png;base64,{img_base64}" style="width:58px; height:58px; margin-right:10px; vertical-align: middle">
            TOTAL REVENUE PER YEAR
        </div>
        ''',
        unsafe_allow_html=True
    )

with col2_header:
    st.markdown("**Past 4 Year Average – Gross Profit / Margin**")

# ---- Columns below headers ----
col1, col2 = st.columns([2, 1])

# ---- Insights section ----
with col1:
    st.markdown(
        '''
        <div style="
            background-color:#f9f9f9; 
            border-left:4px solid #4682B4; 
            padding:12px 20px; 
            margin-bottom:10px;
            border-radius:5px;
            font-family: 'Montserrat', sans-serif;
            color:#333;
            font-size:14px;
        ">
            <strong>Insights:</strong> Revenue is trending positively over the past 4 years. 2025 shows strong growth vs target (+28%) while 2022 shows a slight decline vs previous year (-2.8%).
        </div>
        ''',
        unsafe_allow_html=True
    )

# ---- Left container: 4-year revenue cards ----
with col1:

    def pct_vs_target(actual, target):
        pct = (actual - target) / target * 100
        sign = "+" if pct >= 0 else ""
        color = "#2E8B57" if pct >= 0 else "#FF4500"
        return f"{sign}{pct:.1f}%", color

    def pct_vs_prev(actual, prev):
        if prev is None:
            return None, None
        pct = (actual - prev) / prev * 100
        sign = "+" if pct >= 0 else ""
        color = "#2E8B57" if pct >= 0 else "#FF4500"
        return f"{sign}{pct:.1f}% vs prev", color

    cards_html = ""
    for i in range(4):
        value_m = revenues[i] / 1_000_000
        target_m = targets[i] / 1_000_000

        arrow = "↑" if revenues[i] >= targets[i] else "↓"
        pct_str, pct_color = pct_vs_target(revenues[i], targets[i])

        prev_value = revenues[i+1] if i < 3 else None
        delta_prev_str, delta_prev_color = pct_vs_prev(revenues[i], prev_value)
        delta_html = f'<div style="font-size:13px; color:{delta_prev_color}; margin-top:2px;">{delta_prev_str}</div>' if delta_prev_str else ''

        # Everything inside one parent div
        cards_html += f'<div style="flex:1; text-align:left; margin:0 5px;">' \
                      f'<div style="font-size:18px; color:#333; font-weight:bold; margin-bottom:6px;">{years[i]}</div>' \
                      f'<div style="font-size:18px; font-weight:bold; color:{pct_color};">' \
                      f'<span>&#36;{value_m:.2f}M {arrow}</span> ' \
                      f'<span style="font-size:14px; color:{pct_color}; font-weight:normal;">{pct_str} vs target</span>' \
                      f'</div>' \
                      f'<div style="font-size:13px; color:#666; margin-top:4px;">Target: &#36;{target_m:.2f}M</div>' \
                      f'{delta_html}' \
                      f'</div>'

    st.markdown(
        f'<div style="display:flex; justify-content:space-between; align-items:flex-start; background-color:white; border:1px solid #ccc; border-radius:5px; padding:20px;">{cards_html}</div>',
        unsafe_allow_html=True
    )







# ---- Right container: Past 4 Year Average scorecards ----
with col2:
    st.markdown(
        f"""
        <div style="
            background-color:white;
            border:1px solid #ccc;
            border-radius:5px;
            padding:20px;
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">
            <div style="text-align:center; flex:1;">
                <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>${total_revenue/1_000_000:.2f}M</div>
                <div style="color:#333;">Total Revenue</div>
            </div>
            <div style="text-align:center; flex:1;">
                <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>${total_cogs/1_000_000:.2f}M</div>
                <div style="color:#333;">Total COGS</div>
            </div>
            <div style="text-align:center; flex:1;">
                <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>${gross_profit/1_000_000:.2f}M</div>
                <div style="color:#333;">Gross Profit</div>
            </div>
            <div style="text-align:center; flex:1;">
                <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>{gross_profit_margin:.2%}</div>
                <div style="color:#333;">Gross Profit Margin</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
