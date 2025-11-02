# 🎮 Dota 2 Insights Dashboard

A **Streamlit**-based interactive dashboard that visualizes **top heroes** in the **Dota 2** competitive scene, highlighting **pick rates** and **win rates** from the latest pro game data. This dashboard helps players understand which heroes are currently dominating the meta and which ones to focus on for **Ranked** games.

---

## 🚀 Features

- **📊 Hero Performance Analysis** — Interactive Plotly graph visualizing hero **Pick Rate** vs **Win Rate** in pro games.
- **🏆 Top & Bottom Heroes** — Highlights the **Top 3 Picked** and **Bottom 3 Picked** heroes for easy comparison.
- **🧠 Insights & Tips** — Provides insights on hero performance and strategic recommendations for players.
- **🌍 Hero Guides** — Links to external resources with detailed guides and strategies for top heroes.
- **⚙️ Modular Design** — Easily customizable with updates to hero data, insights, and other game stats.

---

## 🧩 Tech Stack

| Technology | Purpose |
|-------------|----------|
| Streamlit  | Web app framework for the dashboard |
| Pandas     | Data cleaning, transformation, and aggregation |
| Plotly     | Interactive visualization (Pick Rate vs Win Rate chart) |
| Requests   | Fetches real-time data from OpenDota API |
| datetime   | Handles date range calculations for dynamic data updates |

---

Here’s a snapshot of the **Dota 2 Insights Dashboard** built with Streamlit:

![Dashboard Preview](images/dashboard_preview.png)

---

## 📊 Data Source

The data is powered by the **OpenDota API**, which collects and provides comprehensive statistics on Dota 2 matches, including hero performance metrics, pick rates, win rates, and more.

Here’s a look at the website of OpenDota API that powers the entire dashboard:

![Data Preview](images/opendotaapi_preview.png)

> ✨ *This shows how Streamlit can bring Dota 2 pro game data to life — turning raw stats into actionable insights for players!*

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/dota2-insights-dashboard.git
cd dota2-insights-dashboard
