import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import base64
import streamlit.components.v1 as components
import plotly.graph_objects as go

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
targets = [targets_df.iloc[4, col] for col in year_cols]

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
    return f"{sign}{pct:.1f}% vs Prev", color

# ---- Headers outside containers ----
col1_header, col2_header = st.columns([2, 1])
with col1_header:
    st.markdown(
        f'''
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
        <div style="font-family: 'Lato', sans-serif; font-size:30px; color:#AFE1AF; font-weight:900; display:flex; align-items:center; padding-bottom: 10px">
            TOTAL REVENUE PER YEAR
        </div>
        ''',
        unsafe_allow_html=True
    )

with col2_header:
    st.markdown(
        f'''
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
        <div style="font-family: 'Lato', sans-serif; font-size:30px; color:#AFE1AF; font-weight:900; display:flex; align-items:center; padding-bottom: 10px">
            REVENUE VS TARGET – BAR CHART
        </div>
        ''',
        unsafe_allow_html=True
    )


# ---- Columns below headers ----
col1, col2 = st.columns([2, 1])

# ---- Left: Revenue Cards + Double Bars ----
with col1:
    revenue_html = ""
    max_rev = max(revenues)  # for relative widths

    for i in range(4):
        value_m = revenues[i] / 1_000_000
        target_m = targets[i] / 1_000_000
        delta_m = value_m - target_m

        arrow = "↑" if revenues[i] >= targets[i] else "↓"
        pct_str, pct_color = pct_vs_target(revenues[i], targets[i])

        prev_value = revenues[i+1] if i < 3 else None
        pct_prev_str, pct_prev_color = pct_vs_prev(revenues[i], prev_value)
        delta_prev_m = (revenues[i] - prev_value) / 1_000_000 if prev_value is not None else None

        # Side-by-side % vs prev + delta vs prev
        delta_html = ""
        if pct_prev_str or delta_prev_m is not None:
            delta_html += '<div style="display:flex; align-items:center; gap:16px; margin-top:4px;">'
            if pct_prev_str:
                delta_html += f"""<div style="font-size:14px; color:{pct_prev_color}; font-weight:700;">{pct_prev_str}</div>"""
            if delta_prev_m is not None:
                delta_prev_color = "#2E8B57" if delta_prev_m >= 0 else "#FF4500"
                sign = "+" if delta_prev_m > 0 else ""
                delta_html += f"""<div style="font-size:14px; color:{delta_prev_color}; font-weight:600;">{sign}{delta_prev_m:.2f}M Delta vs Prev</div>"""
            delta_html += '</div>'

        revenue_html += f"""
        <div style="flex:1; display:flex; flex-direction:column; justify-content:flex-start; margin-right:24px; margin-bottom:12px;">
            <div style="font-size:23px; font-weight:900; color:#333;">{years[i]}</div>
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="display:flex; flex-direction:column; justify-content:center; line-height:1.2;">
                    <div style="font-size:38px; font-weight:700; color:{pct_color};">${value_m:.2f}M {arrow}</div>
                    <div style="font-size:15px; color:#666; padding-top:2px; padding-bottom:4px">Target: ${target_m:.2f}M</div>
                </div>
                <div style="display:flex; flex-direction:column; justify-content:left; line-height:1.2; text-align:left; padding-bottom:23px">
                    <div style="font-size:15px; color:{pct_color}; font-weight:800; padding-bottom:2px;">{pct_str} vs Target</div>
                    <div style="font-size:15px; color:#2E8B57; font-weight:600;">{delta_m:+.2f}M Delta</div>
                </div>
            </div>
            {delta_html}
        </div>
        """

    # Double horizontal bars under all 4 columns
    bar_html = f"""
    <div style="display:flex; flex-direction:column; gap:2px; margin-top:5px;">
        <!-- First bar line -->
        <div style="display:flex; height:5px; background:#eee; border-radius:6px; overflow:hidden;">
            {"".join([f'<div style="flex:{rev/max_rev}; background:#000000;"></div>' for rev in revenues])}
        </div>

        <!-- Second bar line -->
        <div style="display:flex; height:6px; background:#eee; border-radius:6px; overflow:hidden;">
            {"".join([f'<div style="flex:{rev/max_rev}; background:#000000;"></div>' for rev in revenues])}
        </div>
    </div>
    """

    full_card_html = f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start; 
                background:white; border:1px solid #ccc; border-radius:8px; 
                padding:24px; font-family:'Calibri', sans-serif; height:700px; min-height:700px;">
        <div style="flex:auto; display:flex; flex-direction:column; padding-top:20px">
            <div style="display:flex; justify-content:space-between;">{revenue_html}</div>
            {bar_html}
        </div>
        <div style="flex:0 0 360px; margin-left:24px; font-size:14px; color:#333; padding-top:20px">
            <div style="font-weight:600; font-size:20px; margin-bottom:8px;">Insights</div>
            <ul style="margin:0; padding-left:16px; line-height:1.5;">
                <li>2025 has the highest revenue and has strongest growth</li>
                <li>2024 is also a strong year going beyond previous year's performance</li>
                <li>2023 slightly declined, but target achieved by a huge margin</li>
                <li>2022 is the 2nd best year going beyond the target by 41%</li>
                <li>Strong performance YoY with +31% vs target on average </li>
            </ul>
        </div>
    </div>
    """
    components.html(full_card_html, height=250)


with col2:
    import plotly.graph_objects as go
    import numpy as np

    # Prepare data
    bar_years = years[::-1]
    bar_actuals = [rev / 1_000_000 for rev in revenues[::-1]]
    bar_targets = [tgt / 1_000_000 for tgt in targets[::-1]]

    # Calculate Average
    avg_rev = np.mean(bar_actuals)

    bar_colors = ['#2E8B57' if a >= t else '#FF4500' for a, t in zip(bar_actuals, bar_targets)]

    actual_text = [
        f"<span style='font-size:12px; font-weight:900; color:{'#2E8B57' if a >= t else '#FF4500'};'>({(a-t):+.2f}M Δ)</span><br>"
        f"<b>{a:.2f}M</b>"
        for a, t in zip(bar_actuals, bar_targets)
    ]

    fig = go.Figure()

    # Actual bars
    fig.add_trace(go.Bar(
        x=bar_years, y=bar_actuals, name='Actual',
        marker_color=bar_colors, width=0.4,
        text=actual_text, textposition='outside', cliponaxis=False,
        textfont=dict(size=14),
        customdata=[a - t for a, t in zip(bar_actuals, bar_targets)],
        hovertemplate="Actual: %{y:.2f}M<br>Delta: %{customdata:+.2f}M<extra></extra>"
    ))

    # Target bars
    fig.add_trace(go.Bar(
        x=bar_years, y=bar_targets, name='Target',
        marker_color='#C0C0C0', width=0.4,
        text=[f"<b>{t:.2f}M</b>" for t in bar_targets],
        textposition='outside', cliponaxis=False,
        textfont=dict(size=14),
        hovertemplate='Target: %{y:.2f}M<extra></extra>'
    ))

    # ---- REFINED WHITE AVERAGE LINE ----
    fig.add_shape(
        type="line",
        xref="paper", x0=0, x1=1,
        yref="y", y0=avg_rev, y1=avg_rev,
        line=dict(color="rgba(255, 255, 255, 0.6)", width=1, dash="dot"),
        layer="above" 
    )

    fig.add_annotation(
        xref="paper", x=1,
        yref="y", y=avg_rev,
        text=f"AVG: {avg_rev:.1f}M",
        showarrow=False, 
        xanchor="left", 
        yshift=3, # Increased shift so larger font doesn't touch the line
        xshift=5,
        # Font size now matches the bar labels (14px)
        font=dict(color="rgba(255, 255, 255, 0.8)", size=14, family="Calibri", weight="bold")
    )

    fig.update_layout(
        barmode='group',
        bargap=0.19,
        xaxis_title='',
        yaxis_title='Revenue ($M)',
        yaxis=dict(range=[0, max(bar_actuals + bar_targets) * 1.35]),
        font=dict(family='Calibri', size=14),
        margin=dict(l=10, r=100, t=30, b=30),
        height=300, 
        xaxis=dict(type='category', categoryorder='array', categoryarray=bar_years, autorange='reversed'),
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05)
    )

    st.plotly_chart(fig, use_container_width=True)






# ---- Right container: Past 4 Year Average scorecards ----
# with col2:
#     st.markdown(
#         f"""
#         <div style="
#             background-color:white;
#             border:1px solid #ccc;
#             border-radius:5px;
#             padding:20px;
#             display:flex;
#             justify-content:space-between;
#             align-items:center;
#         ">
#             <div style="text-align:center; flex:1;">
#                 <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>${total_revenue/1_000_000:.2f}M</div>
#                 <div style="color:#333;">Total Revenue</div>
#             </div>
#             <div style="text-align:center; flex:1;">
#                 <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>${total_cogs/1_000_000:.2f}M</div>
#                 <div style="color:#333;">Total COGS</div>
#             </div>
#             <div style="text-align:center; flex:1;">
#                 <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>${gross_profit/1_000_000:.2f}M</div>
#                 <div style="color:#333;">Gross Profit</div>
#             </div>
#             <div style="text-align:center; flex:1;">
#                 <div style='font-size:20px; font-weight:bold; color:#2E8B57;'>{gross_profit_margin:.2%}</div>
#                 <div style="color:#333;">Gross Profit Margin</div>
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
