import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import plotly.graph_objects as go
import math

# ---- Page config ----
st.set_page_config(page_title="FP&A Dashboard", layout="wide")
st.title("FP&A Dashboard – Income Statement")

st.markdown(
    """
    <style>
    .stApp {
        /* A slightly more 'Midnight' feel: Lighter Top-Left, smooth transition to Deep Black */
        background: linear-gradient(135deg, #1a1a2e 0%, #11111b 50%, #050505 100%);
        background-attachment: fixed;
    }
    
    /* Ensures the Streamlit header doesn't cut off the gradient */
    header {background: rgba(0,0,0,0) !important;}
    
    /* Standardize padding for a clean look */
    .stAppViewBlockContainer {
        padding-top: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
    return f"{sign}{pct:.1f}% vs Prev Year", color

# ---- Headers outside containers ----
col1_header, col2_header = st.columns([2, 1])
with col1_header:
    st.markdown(
        f'''
        <div style="font-family: 'Calibri', sans-serif; font-size:30px; color:white; font-weight:900; display:flex; align-items:center; padding-bottom: 10px; padding-left: 15px">
            REVENUE
        </div>
        ''',
        unsafe_allow_html=True
    )

with col2_header:
    st.markdown(
        f'''
        <div style="font-family: 'Calibri', sans-serif; font-size:30px; color:white; font-weight:900; display:flex; align-items:center; padding-bottom: 10px">
            REVENUE VS TARGET
        </div>
        ''',
        unsafe_allow_html=True
    )


# ---- Columns below headers ----
col1, col2 = st.columns([2, 1])

# ---- Left: High-Density Financial Cockpit (DARK THEME) ----
with col1:
    max_rev = max(revenues) 
    max_range = max(revenues + targets)

    # 1. Calculate Dynamic Accuracy for Revenue
    total_revenue = sum(revenues)
    total_target = sum(targets)
    avg_accuracy = ((total_revenue / total_target) - 1) * 100 if total_target != 0 else 0
    accuracy_status = "above" if avg_accuracy >= 0 else "below"

    # 2. Identify Top Year Dynamically
    top_rev_val = max(revenues)
    top_year = years[revenues.index(top_rev_val)]

    
    revenue_html = ""
    for i in range(4):
        value_m = revenues[i] / 1_000_000
        target_m = targets[i] / 1_000_000
        delta_m = value_m - target_m
        achievement_pct = (revenues[i] / targets[i]) * 100 if targets[i] != 0 else 0

        arrow = "↑" if revenues[i] >= targets[i] else "↓"
        pct_str, pct_color = pct_vs_target(revenues[i], targets[i])

        prev_value = revenues[i+1] if i < 3 else None
        pct_prev_str, pct_prev_color = pct_vs_prev(revenues[i], prev_value)
        
        # Dark Mode Adjusted Badges
        badge_bg = "rgba(46, 139, 87, 0.2)" if revenues[i] >= targets[i] else "rgba(255, 69, 0, 0.2)"

        revenue_html += f"""
        <div style="flex:1; display:flex; flex-direction:column; margin-right:15px; font-family:'Calibri', sans-serif;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:20px; font-weight:900; color:#ffffff;">{years[i]}</span>
                <span style="font-size:12px; padding:2px 8px; background:{badge_bg}; color:{pct_color}; border-radius:10px; font-weight:700;">
                    {achievement_pct:.0f}%
                </span>
            </div>
            
            <div style="display:flex; flex-direction:column; line-height:1.1;">
                <div style="font-size:32px; font-weight:700; color:{pct_color};">${value_m:.2f}M <span style="font-size:18px;">{arrow}</span></div>
                
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px; border-bottom:1px solid #333; padding-bottom:6px;">
                    <span style="font-size:14px; color:#aaaaaa;">Target: ${target_m:.2f}M</span>
                    <span style="font-size:14px; color:{pct_color}; font-weight:700;">{pct_str}</span>
                </div>

                <div style="display:flex; justify-content:space-between; margin-top:6px;">
                    <span style="font-size:13px; color:#666666;">vs Prev:</span>
                    <span style="font-size:13px; color:{pct_prev_color or '#666666'}; font-weight:600;">{pct_prev_str or 'N/A'}</span>
                </div>
            </div>
        </div>
        """

    bullet_items = ""
    for i in range(4):
        act_w = (revenues[i] / max_range) * 100
        tgt_p = (targets[i] / max_range) * 100
        t_val = targets[i] / 1_000_000
        b_color = "#2E8B57" if revenues[i] >= targets[i] else "#FF4500"
        
        bullet_items += f"""
        <div style="flex:1; margin-right:15px; display:flex; flex-direction:column; gap:4px; font-family:'Calibri', sans-serif;">
            <div style="display:flex; justify-content:space-between; font-size:14px; font-weight:700; color:#bbbbbb; text-transform:uppercase;">
                <span>Progress</span>
                <span>Goal: {t_val:.1f}M</span>
            </div>
            <div style="position:relative; height:12px; background:#333333; border-radius:2px;">
                <div style="width:{act_w}%; height:100%; background:{b_color}; border-radius:2px; opacity:0.9;"></div>
                <div style="position:absolute; left:{tgt_p}%; top:-4px; width:2px; height:20px; background:#ffffff; z-index:10;"></div>
            </div>
            <div style="font-size:12px; color:#666666; text-align:right; font-style:italic;">
                Target Benchmark
            </div>
        </div>
        """

    bar_html = f"""
    <div style="display:flex; flex-direction:column; gap:2px; margin-top:14px;">
        <div style="display:flex; height:5px; background:#333; border-radius:4px; overflow:hidden;">
            {"".join([f'<div style="flex:{rev/max_rev}; background:#555;"></div>' for rev in revenues])}
        </div>
    </div>
    <div style="display:flex; justify-content:space-between; margin-top:20px;">
        {bullet_items}
    </div>
    """

    full_card_html = f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start; 
                background:#1e1e1e; border:1px solid #333333; border-radius:12px; 
                padding:20px; font-family:'Calibri', sans-serif; margin: 5px; color:white;">
        <div style="flex:auto; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between;">{revenue_html}</div>
            {bar_html}
        </div>
        <div style="flex:0 0 280px; margin-left:25px; border-left:1px solid #333; padding-left:25px;">
            <div style="font-weight:700; font-size:18px; color:#ffffff; margin-bottom:10px;">
                Performance Insights
            </div>
            <ul style="margin:0; padding-left:18px; line-height:1.5; font-size:14px; color:#bbbbbb;">
                <li><b>Top Year:</b> {top_year} at ${top_rev_val/1e6:.2f}M</li>
                <li><b>Momentum:</b> {"Growth trend" if revenues[0] > revenues[1] else "Stability focus"} sustained</li>
                <li><b>Accuracy:</b> Avg {abs(avg_accuracy):.0f}% {accuracy_status} target</li>
                <li><b>Risk:</b> {years[revenues.index(min(revenues))]} saw lowest volume</li>
            </ul>
            
            <div style="margin-top:18px; padding:10px; background:#2a2a2a; border-radius:6px; border: 1px dashed #444;">
                <div style="font-size:11px; color:#888; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">Global Status</div>
                <div style="font-size:16px; font-weight:800; color:#2E8B57;">OUTPERFORMING</div>
            </div>
        </div>
    </div>
    """
    
    components.html(full_card_html, height=260)


with col2:
    # Prepare data
    bar_years = years[::-1]
    bar_actuals = [rev / 1_000_000 for rev in revenues[::-1]]
    bar_targets = [tgt / 1_000_000 for tgt in targets[::-1]]

    x_indices = np.arange(len(bar_years))
    actual_bar_offset = 0.21 

    avg_rev = np.mean(bar_actuals)
    bar_colors = ['#2E8B57' if a >= t else '#FF4500' for a, t in zip(bar_actuals, bar_targets)]

    actual_text = [
        f"<span style='font-size:12px; font-weight:900; color:{'#2E8B57' if a >= t else '#FF4500'}; font-family:Calibri;'>({(a-t):+.2f}M Δ)</span><br>"
        f"<b style='font-family:Calibri;'>{a:.2f}M</b>"
        for a, t in zip(bar_actuals, bar_targets)
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x_indices - actual_bar_offset, 
        y=bar_actuals, name='Actual',
        marker_color=bar_colors, width=0.4,
        text=actual_text, textposition='outside', cliponaxis=False,
        textfont=dict(size=13, family="Calibri"),
        customdata=[a - t for a, t in zip(bar_actuals, bar_targets)],
        hovertemplate="Actual: %{y:.2f}M<br>Delta: %{customdata:+.2f}M<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=x_indices + actual_bar_offset, 
        y=bar_targets, name='Target',
        marker_color='#C0C0C0', width=0.4,
        text=[f"<b>{t:.2f}M</b>" for t in bar_targets],
        textposition='outside', cliponaxis=False,
        textfont=dict(size=13, family="Calibri"),
        hovertemplate='Target: %{y:.2f}M<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=x_indices - actual_bar_offset, 
        y=bar_actuals,
        mode='lines+markers',
        name='Trend',
        line=dict(color='rgba(255, 255, 255, 0.6)', width=2, shape='linear'),
        marker=dict(size=6, color='#FFFFFF'),
        hoverinfo='skip'
    ))

    fig.add_shape(
        type="line",
        xref="paper", x0=0, x1=1,
        yref="y", y0=avg_rev, y1=avg_rev,
        line=dict(color="rgba(255, 255, 255, 0.5)", width=1, dash="dot"),
        layer="above" 
    )

    fig.add_annotation(
        xref="paper", x=1,
        yref="y", y=avg_rev,
        text=f"AVG: {avg_rev:.1f}M",
        showarrow=False, 
        xanchor="left", 
        yshift=3, 
        xshift=5,
        font=dict(color="white", size=11, family="Calibri", weight="normal")
    )

    top_tick = math.ceil(max(bar_actuals + bar_targets))
    y_range_limit = top_tick + 0.1

    fig.update_layout(
        barmode='overlay',
        # --- NEW BACKGROUND SETTINGS ---
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # -------------------------------
        font=dict(family='Calibri', size=12, color="white"), 
        yaxis=dict(
            title=dict(text='Revenue ($M)', font=dict(color="white", family="Calibri")),
            dtick=1,
            range=[0, y_range_limit],
            tickfont=dict(color="white", family="Calibri"),
            # Remove grid lines for a cleaner look on gradient
            showgrid=False,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        xaxis=dict(
            title=dict(text='', font=dict(color="white", family="Calibri")),
            tickmode='array',
            tickvals=x_indices,
            ticktext=bar_years,
            autorange='reversed',
            tickfont=dict(color="white", family="Calibri"),
            # Remove vertical grid lines
            showgrid=False
        ),
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="top", 
            y=1.20, 
            xanchor="left", 
            x=1.05,
            font=dict(color="white", family="Calibri"),
            bgcolor='rgba(0,0,0,0)' # Make legend background invisible too
        ),
        margin=dict(l=0, r=100, t=30, b=0),
        height=266
    )

    st.plotly_chart(fig, use_container_width=True)

# ---- COGS SECTION DATA ----
total_25 = df.iloc[9, 2]
total_24 = df.iloc[9, 3]
total_23 = df.iloc[9, 4]
total_22 = df.iloc[9, 5]

cogs_rows = [
    {"label": "Cost of Product Sales", "idx": 6, "color": "#5C3E94"}, 
    {"label": "Cost of Services", "idx": 7, "color": "#1E90FF"},      
    {"label": "Logistics / Fulfillment", "idx": 8, "color": "#FFA500"}, 
    {"label": "TOTAL COGS", "idx": 9, "color": "#FFFAA0"}                
]

table_rows_html = ""
# Using enumerate so we can target specific row numbers
for i, item in enumerate(cogs_rows):
    vals = [df.iloc[item["idx"], i_col] for i_col in [2, 3, 4, 5]]
    totals = [total_25, total_24, total_23, total_22]
    
    is_total = "TOTAL" in item["label"]
    
    # Default styling for rows 1-3
    top_space = "0px"
    bottom_space = "0px"
    label_font_size = "15px"
    value_font_size = "15px" 
    label_color = "#cccccc"
    value_color = "#ffffff" 
    row_style = ""

    # 1. Spacing for Row 1 (Index 0) - Push away from header
    if i == 0:
        top_space = "10px"
    
    # 2. REMOVED GAP: bottom_space for Row 3 is now 0px to keep it tight to TOTAL
    if i == 2:
        bottom_space = "0px" 

    # 3. Styling for TOTAL COGS Row (Index 3)
    if is_total:
        label_color = "#FFFAA0"
        label_font_size = "24px"
        value_color = "#FFFAA0"
        value_font_size = "24px"
        
        # REMOVED border-top here to take away the break line
        row_style = "font-weight: 800;" 
        top_space = "16px" 
    
    cells = ""
    for val, tot in zip(vals, totals):
        pct = (val / tot * 100) if tot != 0 else 0
        bar_width = f"{pct}%"
        
        cells += f"""
        <td style="text-align: center; padding: {top_space} 5px {bottom_space} 5px;">
            <div style="display: flex; flex-direction: column; align-items: flex-start; min-width: 90px; font-family: 'Calibri', sans-serif;">
                <div style="font-weight: 700; font-size: {value_font_size}; color: {value_color};">${val/1e6:.2f}M</div>
                <div style="display: flex; align-items: center; width: 100%; margin-top: 2px;">
                    <div style="flex-grow: 1; height: 4px; background: #444; border-radius: 2px; overflow: hidden; margin-right: 5px;">
                        <div style="width: {bar_width}; height: 100%; background: {item['color']};"></div>
                    </div>
                    <span style="color: #888; font-size: 11px;">{pct:.0f}%</span>
                </div>
            </div>
        </td>
        """

    table_rows_html += f"""
    <tr style="{row_style} font-family: 'Calibri', sans-serif;">
        <td style="text-align: left; padding-left: 10px; padding-top: {top_space}; padding-bottom: {bottom_space}; width: 22%; font-size: {label_font_size}; color: {label_color};">
            {item['label']}
        </td>
        {cells}
    </tr>
    """

col_cogs_left, col_cogs_right = st.columns([2, 1])

with col_cogs_left:
    st.markdown(
        f'''<div style="font-family: 'Calibri', sans-serif; font-size:32px; color:white; font-weight:900; padding-bottom: 8px; margin-left: 18px;">
            COST OF GOODS SOLD
        </div>''', unsafe_allow_html=True
    )

    integrated_cogs_card = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; }}
        .cogs-container {{
            display: flex; background: #1e1e1e; border: 1px solid #333333; border-radius: 12px; 
            padding: 20px; font-family: 'Calibri', sans-serif; box-sizing: border-box; height: 250px;
            width: calc(100% - 30px); margin-left: 15px; margin-right: 15px; margin-top: 5px; margin-bottom: 5px; color: white;
        }}
    </style>
    <div class="cogs-container">
        <div style="flex: 1; min-width: 0;">
            <table style="width: 100%; border-collapse: collapse; table-layout: fixed; font-family: 'Calibri', sans-serif;">
                <thead>
                    <tr style="color: #FFFFFF; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #444;">
                        <th style="text-align: left; padding-bottom: 8px; padding-left: 10px; width: 25%;">Description</th>
                        <th style="text-align: center; padding-bottom: 8px;">2025</th>
                        <th style="text-align: center; padding-bottom: 8px;">2024</th>
                        <th style="text-align: center; padding-bottom: 8px;">2023</th>
                        <th style="text-align: center; padding-bottom: 8px;">2022</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html.replace('height: 42px;', 'height: 40px;')}
                </tbody>
            </table>
        </div>
        <div style="flex: 0 0 280px; margin-left: 25px; border-left: 1px solid #444; padding-left: 25px;">
            <div style="font-weight: 700; font-size: 18px; color: #ffffff; margin-bottom: 10px;">Performance Insights</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.5; font-size: 14px; color: #bbbbbb;">
                <li><b>Efficiency:</b> Costs scaling below revenue</li>
                <li><b>Logistics:</b> Fulfillment flat vs volume</li>
                <li><b>Services:</b> 2025 labor optimized</li>
                <li><b>Risk:</b> Material price volatility</li>
            </ul>
            <div style="margin-top: 18px; padding: 10px; background: #2a2a2a; border-radius: 6px; border: 1px dashed #444;">
                <div style="font-size: 11px; color: #888888; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Profitability Status</div>
                <div style="font-size: 16px; font-weight: 800; color: #2E8B57;">SUSTAINABLE</div>
            </div>
        </div>
    </div>
    """
    components.html(integrated_cogs_card, height=260)


with col_cogs_right:
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go # Ensure go is imported

    plot_years = [2025, 2024, 2023, 2022]
    chart_cols = [2, 3, 4, 5] 
    
    # --- FIXED: Changed "Total" to "TOTAL" to match your label ---
    labels = [item["label"] for item in cogs_rows if "TOTAL" not in item["label"]]
    colors = ["#5C3E94", "#1E90FF", "#FFA500"]

    fig_row = make_subplots(rows=1, cols=4, specs=[[{'type':'domain'}]*4], horizontal_spacing=0.01)

    for i, year_col in enumerate(chart_cols):
        # --- FIXED: Changed "Total" to "TOTAL" here as well ---
        values = [df.iloc[item["idx"], year_col] for item in cogs_rows if "TOTAL" not in item["label"]]
        
        fig_row.add_trace(
            go.Pie(
                labels=labels, values=values, hole=0.65,
                marker=dict(colors=colors, line=dict(color='#111', width=1)),
                textinfo='percent', textposition='inside',
                textfont=dict(size=14, color="white", weight="bold", family="Calibri"),
                title=dict(
                    text=f"<b>{plot_years[i]}</b>", 
                    font=dict(size=20, color="white", family="Calibri"), 
                    position="middle center"
                ),
                showlegend=(i == 0)
            ), row=1, col=i+1
        )

        fig_row.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h", 
                    yanchor="top", 
                    y=-0.1, 
                    xanchor="center", 
                    x=0.5, 
                    # --- UPDATED: Increased size from 10 to 12 ---
                    font=dict(color="white", size=12, family="Calibri")
                    # ---------------------------------------------
                ),
                margin=dict(l=10, r=10, t=30, b=0), 
                height=270, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Calibri")
            )

    st.markdown(
        f'''<div style="font-family: 'Calibri', sans-serif; font-size:32px; color:white; font-weight:900; padding-bottom: 5px; margin-left: 5px;">
            COGS DISTRIBUTION
        </div>''', unsafe_allow_html=True
    )
    st.plotly_chart(fig_row, use_container_width=True, config={'displayModeBar': False})



# ---- GROSS PROFIT REPORTING DATA ----
gp_actuals = [df.iloc[11, col] for col in [2, 3, 4, 5]]    
gpm_actuals = [df.iloc[12, col] for col in [2, 3, 4, 5]]   
years_labels = ["2025", "2024", "2023", "2022"]

gp_grid_html = ""

for i in range(4):
    val_m = gp_actuals[i] / 1e6
    mgn = gpm_actuals[i] * 100 if gpm_actuals[i] < 1 else gpm_actuals[i]
    
    if mgn >= 40:
        accent_color = "#2E8B57" 
        card_bg = "rgba(46, 139, 87, 0.12)"
    elif mgn >= 30:
        accent_color = "#FFD700" 
        card_bg = "rgba(255, 215, 0, 0.08)"
    else:
        accent_color = "#FF4500" 
        card_bg = "rgba(255, 69, 0, 0.08)"

    # Increased Math for larger Gauge
    gauge_val = min(max(mgn, 0), 100)
    # Radius 24 semi-circle approx 75.4
    dash_array = 75.4
    dash_offset = dash_array - (gauge_val / 100 * dash_array)

    if i < 3:
        diff = gp_actuals[i] - gp_actuals[i+1]
        trend_str = f"{'↑' if diff >= 0 else '↓'} YoY"
        trend_color = "#2E8B57" if diff >= 0 else "#FF4500"
    else:
        trend_str = "N/A"
        trend_color = "#666"

    gp_grid_html += f"""
    <div style="flex: 1; padding: 10px; background: {card_bg}; border: 1px solid {accent_color}44; border-radius: 12px; margin-right: 8px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; min-width: 0; box-sizing: border-box;">
        <div style="width: 100%; display: flex; justify-content: space-between; margin-bottom: 0px;">
            <span style="font-size: 18px; color: #888; font-weight: 800;">{years_labels[i]}</span>
            <span style="font-size: 14px; color: {trend_color}; font-weight: 800;">{trend_str}</span>
        </div>
        
        <div style="font-size: 36px; font-weight: 900; color: white; margin-bottom: 2px; letter-spacing: -1.5px;">${val_m:.2f}M</div>

        <div style="position: relative; width: 140px; height: 75px; display: flex; justify-content: center; align-items: flex-end;">
            <svg viewBox="0 0 60 32" style="width: 140px; height: 75px; display: block;">
                <path d="M 6 30 A 24 24 0 0 1 54 30" fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>
                <path d="M 6 30 A 24 24 0 0 1 54 30" fill="none" stroke="{accent_color}" stroke-width="8" 
                      stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}" stroke-linecap="round" 
                      style="transition: stroke-dashoffset 1s ease-out;"/>
            </svg>
            <div style="position: absolute; bottom: 2px; width: 100%; text-align: center; font-size: 24px; font-weight: 900; color: {accent_color};">
                {mgn:.0f}%
            </div>
        </div>
        
        <div style="font-size: 10px; color: #aaa; text-transform: uppercase; font-weight: bold; margin-top: 4px; letter-spacing:0.5px;">GP Margin</div>
    </div>
    """

col_p_left, col_p_right = st.columns([2, 1])

with col_p_left:
    st.markdown(
        f'''<div style="font-family: 'Calibri', sans-serif; font-size:32px; color:white; font-weight:900; padding-bottom: 8px; margin-left: 18px; margin-top:15px;">
            GROSS PROFIT
        </div>''', unsafe_allow_html=True
    )

    integrated_gp_card = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; }}
        .gp-container {{
            display: flex; background: #1e1e1e; border: 1px solid #333333; border-radius: 12px; 
            padding: 20px; font-family: 'Calibri', sans-serif; box-sizing: border-box; height: 250px;
            width: calc(100% - 30px); margin-left: 15px; margin-right: 15px; margin-top: 5px; color: white;
        }}
    </style>
    <div class="gp-container">
        <div style="flex: 1; display: flex; align-items: stretch; margin-right: 0px; min-width: 0;">
            {gp_grid_html}
        </div>

        <div style="flex: 0 0 280px; margin-left: 25px; border-left: 1px solid #444; padding-left: 25px;">
            <div style="font-weight: 700; font-size: 18px; color: #ffffff; margin-bottom: 10px;">Performance Insights</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.5; font-size: 14px; color: #bbbbbb;">
                <li><b>Portfolio Growth:</b> ${ (gp_actuals[0]-gp_actuals[3])/1e6:+.1f}M gain</li>
                <li><b>Peak Efficiency:</b> {years_labels[np.argmax(gpm_actuals)]}</li>
                <li><b>Avg Margin:</b> {np.mean(gpm_actuals)*100:.1f}%</li>
                <li><b>Trend:</b> Strong Yield Arch</li>
            </ul>
            <div style="margin-top: 18px; padding: 10px; background: #2a2a2a; border-radius: 6px; border: 1px dashed #444;">
                <div style="font-size: 11px; color: #888888; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Profitability Status</div>
                <div style="font-size: 16px; font-weight: 800; color: #2E8B57;">STABLE</div>
            </div>
        </div>
    </div>
    """
    components.html(integrated_gp_card, height=265)



# ---- DATA EXTRACTION (B5, B10, B12, B13) ----
avg_rev_val = df.iloc[4, 1]   
avg_cogs_val = df.iloc[9, 1]  
avg_gp_val = df.iloc[11, 1]   
avg_gpm_val = df.iloc[12, 1]  

# Safety check for percentage format
display_gpm = avg_gpm_val * 100 if avg_gpm_val <= 1.0 else avg_gpm_val

with col_p_right:
    # Forced Calibri Header
    st.markdown(
        f'''
        <style>
            @import url('https://fonts.cdnfonts.com/css/calibri'); /* Standard web-safe backup */
        </style>
        <div style="
            font-family: 'Calibri', 'Calibri-Bold', 'Candara', 'Segoe UI', sans-serif !important; 
            font-size: 32px; 
            color: white; 
            margin-top: 25px; 
            letter-spacing: 1px; 
            text-transform: uppercase;
            -webkit-font-smoothing: antialiased;
        ">
            PAST 4 YEARS AVERAGE
        </div>
        ''', unsafe_allow_html=True
    )
    
    summary_html = f"""
    <style>
        /* Force Calibri at the root level */
        * {{
            font-family: 'Calibri', 'Candara', 'Segoe UI', sans-serif !important;
        }}
        
        body {{ 
            margin: 0; padding: 0; background-color: transparent; 
            color: white; overflow: hidden; 
        }}
        .summary-wrapper {{
            display: flex;
            flex-direction: column;
            height: 265px;
            padding-top: 20px;
            box-sizing: border-box;
        }}
        .top-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 25px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .stat-group {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .label {{ 
            font-size: 14px; 
            color: #FFFFFF; 
            text-transform: uppercase; 
            font-weight: 800; 
            letter-spacing: 1.5px;
            margin-bottom: 8px;
            opacity: 0.9;
        }}
        .value {{ 
            font-size: 29px; 
            font-weight: 900; 
            letter-spacing: -1px;
            color: white;
        }}
        .hero-section {{
            padding: 20px;
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            background: linear-gradient(90deg, rgba(46, 139, 87, 0.15) 0%, rgba(0,0,0,0) 100%);
            border-left: 4px solid #2E8B57;
            border-radius: 0 12px 12px 0;
        }}
        .margin-label {{
            font-size: 14px;
            color: #2E8B57;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .margin-value {{
            font-size: 54px;
            font-weight: 900;
            line-height: 1;
            color: white;
            display: flex;
            align-items: baseline;
        }}
        .pct-sign {{
            font-size: 24px;
            color: #2E8B57;
            margin-left: 5px;
        }}
    </style>
    
    <div class="summary-wrapper">
        <div class="top-row">
            <div class="stat-group">
                <div class="label">Total Revenue</div>
                <div class="value">${avg_rev_val/1e6:.2f}M</div>
            </div>
            
            <div style="width: 1px; height: 45px; background: rgba(255,255,255,0.1); margin: 0 15px;"></div>

            <div class="stat-group">
                <div class="label">Total COGS</div>
                <div class="value">${avg_cogs_val/1e6:.2f}M</div>
            </div>

            <div style="width: 1px; height: 45px; background: rgba(255,255,255,0.1); margin: 0 15px;"></div>

            <div class="stat-group">
                <div class="label">Gross Profit</div>
                <div class="value" style="color: #2E8B57;">${avg_gp_val/1e6:.2f}M</div>
            </div>
        </div>

        <div class="hero-section">
            <div class="margin-label">Gross Profit Margin</div>
            <div class="margin-value">
                {display_gpm:.1f}<span class="pct-sign">%</span>
            </div>
        </div>
    </div>
    """
    components.html(summary_html, height=265)