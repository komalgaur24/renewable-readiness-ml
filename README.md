# 🌍 Renewable Energy Adoption Readiness Score

An end-to-end Machine Learning system that predicts how ready a country is to adopt renewable energy.

## 🔹 Live Demo
👉 [Coming Soon - Streamlit Deploy Link]

## 🔹 Problem
Countries don't adopt renewable energy equally due to:
- Economic differences
- Infrastructure gaps  
- Energy demand variations

## 🔹 Solution
ML system that analyzes country-level indicators and classifies each country as:
- 🟢 **High Readiness**
- 🟡 **Medium Readiness**  
- 🔴 **Low Readiness**

## 🔹 Tech Stack
| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| ML Models | Scikit-learn |
| Database | MongoDB |
| Dashboard | Streamlit |
| Data Sources | World Bank + Kaggle |
| Visualization | Plotly |

## 🔹 Features
- 🗺️ Interactive world map
- 📊 Score distribution charts
- 🔬 Country deep-dive with radar chart
- 🤖 Model performance insights
- 🔮 Predict any custom scenario

## 🔹 ML Models
| Model | Accuracy |
|---|---|
| Logistic Regression | 94.29% |
| Random Forest | 74.29% |
| Decision Tree | 60.00% |

## 🔹 Data Sources
- [Kaggle - Global Sustainable Energy](https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy)
- [World Bank - GDP per Capita](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)
- [World Bank - Electricity Access](https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS)
- [World Bank - Urban Population](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS)
- [World Bank - Renewable Share](https://data.worldbank.org/indicator/EG.FEC.RNEW.ZS)

## 🔹 Project Structure
```
renewable-readiness/
├── data/
│   └── raw/          ← CSV data files (download separately)
├── src/
│   ├── data_collection.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── label_creation.py
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
├── models/           ← Saved ML models (generated after training)
├── dashboard/
│   └── app.py        ← Streamlit dashboard
├── requirements.txt
└── README.md
```

## 🔹 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/renewable-readiness-ml.git
cd renewable-readiness-ml
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download datasets
- [Kaggle Dataset](https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy) → place in `data/raw/`
- World Bank CSVs → place in `data/raw/`

### 5. Run pipeline
```bash
python src/data_collection.py
python src/preprocessing.py
python src/feature_engineering.py
python src/label_creation.py
python src/train.py
python src/evaluate.py
python src/predict.py
```

### 6. Launch dashboard
```bash
streamlit run dashboard/app_v2.py
```

## 🔹 Environment Variables
Create `.env` file:
```
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=renewable_readiness
```

