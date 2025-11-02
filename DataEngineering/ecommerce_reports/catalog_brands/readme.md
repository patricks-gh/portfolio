# 🧴 Top Brands Report — The Beauty Hub

A **Streamlit**-based interactive report that visualizes the **dominant brands based on product count** from *The Beauty Hub’s* product catalog, powered directly by data from **Google Sheets**.  
This dashboard highlights which brands dominate the catalog, grouping smaller contributors into an “Others” category for clarity and insight.

---

## 🚀 Features

- **🔗 Live Google Sheets Integration** — Automatically pulls the latest product data using the `gspread` API.  
- **📊 Dynamic Pie Chart Visualization** — Interactive Plotly donut chart showing top brands vs. others.  
- **🏆 Top Brand Highlights** — Displays logo cards for the top three brands with optional branding images.  
- **📈 Cumulative Analysis** — Breaks down product contribution percentages per brand and identifies top 60% performers.  
- **📁 Modular Structure** — Designed for easy maintenance and customization (logo handling, threshold tuning, etc.).

---

## 🧩 Tech Stack

| Technology | Purpose |
|-------------|----------|
| Streamlit | Web app framework for the dashboard |
| Pandas | Data cleaning and aggregation |
| Plotly | Interactive visualization (donut chart) |
| GSpread | Connects to Google Sheets API |
| Base64 | Encodes local images for web display |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/beautyhub-topbrands-report.git
cd catalog_brands
