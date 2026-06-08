# 💊 Pharmacy Intelligence System

## 🛠 Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.12 |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Plotly |
| Database | SQLite |
| Dashboard | Streamlit |
| Forecasting | Prophet |
| Version Control | Git / GitHub |

---

## 📊 Dashboard Pages

| Page | What it shows |
|------|---------------|
| 🏠 Home | KPI cards, revenue trend, branch ranking |
| 📈 Sales | Top medicines, heatmap, payment mix, live filters |
| 📦 Inventory | Stock alerts, expiry risk, reorder table |
| 👥 Customers | RFM segments, age/gender analysis, top customers |

---

## 🔍 SQL Techniques Used

- CTEs (Common Table Expressions)
- Window Functions — RANK(), LAG(), SUM() OVER()
- CASE WHEN for business segmentation
- Multi-table JOINs
- Subqueries for filtered aggregations

---

## 🔮 Forecasting Results

- Trained Prophet models for 3 categories
- 6-month forward predictions with 95% confidence intervals
- Generated automated business recommendations

---

## ⚙️ How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/lohith-214/pharmacy-intel.git
cd pharmacy-intel

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset
python data/generate_dataset.py

# 4. Run EDA pipeline
python notebooks/eda_pipeline.py

# 5. Load database
python sql/load_database.py

# 6. Run forecasting
python models/forecasting.py

# 7. Launch dashboard
streamlit run app/streamlit_app.py
```


---

## 👤 Author

# Lohith Goud

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/b-lohith-goud-7582ba301/)
[![GitHub](https://img.shields.io/badge/GitHub-lohith--214-black)](https://github.com/lohith-214)