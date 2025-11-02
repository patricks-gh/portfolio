import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from gspread_dataframe import get_as_dataframe
import os
import base64


# ---- CONNECT TO GOOGLE SHEETS ----
gc = gspread.service_account(filename="../../../python/auth_keys/service_account.json")
sheet = gc.open("Admin - The Beauty Hub").worksheet("productlist")
df_sheet = get_as_dataframe(sheet, evaluate_formulas=True).dropna(how='all')

# --- VALIDATION ---
required_cols = ["Brand", "Product Name", "Status"]
for col in required_cols:
    if col not in df_sheet.columns:
        raise ValueError(f"Missing Column: {col}")

# ---- PROCESS DATA ----
# Filter only active products
df_active = df_sheet[df_sheet["Status"] == "Active"]

# Aggregate product count per brand
brand_summary = (
    df_active.groupby("Brand")
    .size()
    .reset_index(name="Products")
    .sort_values(by="Products", ascending=False)
)

# Calculate percentage, cumulative percentage, and rank
total_products = brand_summary["Products"].sum()
brand_summary["%"] = brand_summary["Products"] / total_products * 100
brand_summary["Cumulative"] = brand_summary["%"].cumsum()
brand_summary["Rank"] = brand_summary["Products"].rank(method="min", ascending=False).astype(int)

# ---- ADD 'OTHERS' CATEGORY ----
top_brands = brand_summary[brand_summary["Cumulative"] < 61].copy()
others = brand_summary[brand_summary["Cumulative"] >= 61].copy()

if not others.empty:
    others_row = pd.DataFrame({
        "Brand": ["Others"],
        "Products": [others["Products"].sum()],
        "%": [others["%"].sum()],
        "Cumulative": [100],
        "Rank": [len(top_brands) + 1]
    })
    top_brands = pd.concat([top_brands, others_row], ignore_index=True)

# Use top_brands for plotting
df_plot = top_brands
df_plot["%"] = df_plot["%"].round(2)
df_plot["Cumulative"] = df_plot["Cumulative"].round(2)

# ---- COLORS ----
colors = [
    "#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A","#19D3F3",
    "#FF6692","#B6E880","#FF97FF","#FECB52","#636EFA","#EF553B",
    "#00CC96","#AB63FA","#FFA15A","#19D3F3"
][:len(df_plot)]  # adjust dynamically

# ---- CREATE FIGURE ----
fig = go.Figure()

# Inner Pie - bigger domain to make pie bigger
fig.add_trace(go.Pie(
    labels=df_plot["Brand"],
    values=df_plot["Products"],
    hole=0.3,
    text=df_plot["Products"],
    textinfo="text",
    textposition="inside",
    insidetextorientation="radial",
    insidetextfont=dict(size=18),
    marker=dict(colors=colors, line=dict(color="white", width=2)),
    hovertemplate="%{label}<br>%{value} products<br>%{percent}",
    showlegend=True,
    sort=False,
    direction="clockwise",
    rotation=0,
    domain=dict(x=[0, 0.9], y=[0.15, 1])
))

# Outer Pie Labels - match the same domain as inner pie
fig.add_trace(go.Pie(
    labels=df_plot["Brand"],
    values=df_plot["Products"],
    hole=0.3,
    text=[f"{b}<br>{p:.1f}%" for b, p in zip(df_plot["Brand"], df_plot["%"])],
    textinfo="text",
    textposition="outside",
    outsidetextfont=dict(size=14),
    marker=dict(colors=["rgba(0,0,0,0)"]*len(df_plot), line=dict(color="rgba(0,0,0,0)", width=0)),
    hoverinfo="none",
    showlegend=False,
    sort=False,
    direction="clockwise",
    rotation=0,
    domain=dict(x=[0, 0.9], y=[0.15, 1])
))

# Layout: increased height, margin, legend on the right
fig.update_layout(
    title=(
        "<span style='color:darkgray'><b>Inside the pie:</b></span> product count"
        "<br>"
        "<span style='color:darkgray'><b>Outside the pie:</b></span> brand + %."
    ),
    title_x=0.01,
    title_y=0.88,
    title_font_size=20,
    legend=dict(
        orientation="v",
        y=0.73,
        x=0.8,  # legend shifted right to avoid overlap
        xanchor="left",
        yanchor="middle",
        font=dict(size=16),
        title=dict(text="Brands", font=dict(size=18, color="white"))
    ),
    margin=dict(t=80, b=120, l=40, r=40),
    height=950,
    width=1000,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)



# ---- STREAMLIT APP ----
st.set_page_config(page_title="Top Brands Pie Chart", layout="wide")
st.title(":rainbow[Top Brands by Product Count (Top Contributors + Others)]")
st.write("\n\n")  # spacing

col1, col2 = st.columns([2.1, 1.5])

with col1:
    st.plotly_chart(fig, use_container_width=True)

shown_products = df_plot[df_plot["Brand"] != "Others"]["Products"].sum()

with col2:
    st.markdown("#### :sparkles: 📊 SUMMARY :sparkles:")
    st.markdown(f"**Total Products Shown:** {df_plot['Products'].sum()}")
    st.markdown(
        f"The brands that are shown make up roughly **60%** "
        f"(*{shown_products} products*) of all listed products, "
        "with the rest grouped under 'Others'."
    )
    st.markdown(f"## :rainbow[**Top Brand:** {df_plot.iloc[0]['Brand']}]")
    # st.markdown(f"**🏆 Top 3 Brands:** {', '.join(df_plot['Brand'].head(3).tolist())} 🥈🥉")

    
    st.subheader("🏆 Top 3 Brand Highlights")

    # Get absolute path to the logos folder
    base_path = os.path.dirname(__file__)
    logo_path = os.path.join(base_path, "logos") 

    # Mapping brand name → logo file path
    brand_logos = {
        "BREMOD": os.path.join(logo_path, "bremod.png"),
        "RYXSKIN SINCERITY": os.path.join(logo_path, "ryx.png"),
        "BRILLIANT SKIN": os.path.join(logo_path, "brilliant.png"),
    }

    top3 = df_plot["Brand"].head(3).tolist()
    cols = st.columns(3)

    bg_color = "#1a1a1a"  # very dark gray
    text_color = "#ffffff"

    def img_to_base64(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    for idx, brand in enumerate(top3):
        with cols[idx]:
            logo_path_local = brand_logos.get(brand)
            if logo_path_local and os.path.exists(logo_path_local):
                logo_base64 = img_to_base64(logo_path_local)
                logo_html = f"data:image/png;base64,{logo_base64}"
            else:
                # fallback placeholder
                logo_html = "https://via.placeholder.com/150"

            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color};
                    padding: 15px;
                    border-radius: 12px;
                    text-align: center;
                ">
                    <img src="{logo_html}" style="max-width: 100%; height: auto; display: block; margin-left: auto; margin-right: auto;">
                    <p style="color: {text_color}; font-weight: bold; margin-top: 8px;">{brand}</p>
                </div>
                """,
                unsafe_allow_html=True
            )



    st.markdown("""
    ---
    #### Insights & Context
    - This provides a sense of familiarity with the product brands.
    - This chart highlights to identify which brands contribute most to the active product catalog.
    - You can identify trends in brand dominance and product variety.
    - 'Others' groups less significant brands together for clarity.
    - Consider expanding marketing or inventory for top-performing brands.
    """)

    st.markdown("---")  # divider line just like the one above Summary

    # Display the brands that were grouped under "Others"
    if not others.empty:
        with st.expander("🧴 View brands included in 'Others' (click to expand)", expanded=False):
            other_brands = others["Brand"].tolist()

            # Create 4 columns for compact layout
            cols = st.columns(4)
            for idx, brand in enumerate(other_brands):
                with cols[idx % 4]:
                    st.markdown(f"<span style='color:gray'>• {brand}</span>", unsafe_allow_html=True)

    
    st.caption("The Beauty Hub")