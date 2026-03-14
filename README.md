# 🌍 Renewable Energy Adoption Readiness Score

An end-to-end Machine Learning system that predicts how ready
a country is to adopt renewable energy.

## 🔹 Live Demo
👉 Coming Soon

## 🔹 Problem
Countries don't adopt renewable energy equally due to:
- Economic differences
- Infrastructure gaps
- Energy demand variations

## 🔹 Solution
ML system that classifies each country as:
- 🟢 High Readiness
- 🟡 Medium Readiness
- 🔴 Low Readiness

## 🔹 Tech Stack
- Python, Scikit-learn, MongoDB, Streamlit, Plotly
- Data: World Bank + Kaggle

## 🔹 Models & Accuracy
| Model | Accuracy |
|---|---|
| Logistic Regression | 94.29% |
| Random Forest | 74.29% |
| Decision Tree | 60.00% |

## 🔹 Features
- 🌍 Interactive 3D Globe
- ⚔️ Country Battle Mode
- 🔮 Future 2050 Predictor
- 🎯 Policy Recommendation Engine
- 📄 Auto Report Generator
- 🏆 Country Leaderboard
- ⚡ Custom Prediction Tool
- 🎨 4 Personalized Themes

## 🔹 Data Sources
- Kaggle Global Sustainable Energy Dataset
- World Bank Development Indicators

## 🔹 Setup & Run

### 1. Clone
\`\`\`bash
git clone https://github.com/komalgaur24/renewable-readiness-ml.git
cd renewable-readiness-ml
\`\`\`

### 2. Setup
\`\`\`bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### 3. Add data files to data/raw/
Download from Kaggle and World Bank

### 4. Run pipeline
\`\`\`bash
python src/data_collection.py
python src/preprocessing.py
python src/feature_engineering.py
python src/label_creation.py
python src/train.py
python src/evaluate.py
python src/predict.py
\`\`\`

### 5. Launch dashboard
\`\`\`bash
streamlit run dashboard/app_v2.py
\`\`\`

## 🔹 Environment Variables
Create `.env` file:
\`\`\`
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=renewable_readiness
\`\`\`
