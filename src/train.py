import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

INPUT_FILE   = "data/raw/labeled_data.csv"
RANDOM_STATE = 42
FEATURE_COLS = [
    "log_gdp_per_capita", "urban_population_pct",
    "log_energy_use_per_capita", "electricity_access_pct",
    "renewable_share_pct", "energy_pressure_index", "infrastructure_score",
]

def train():
    print("🤖 Training ML Models...\n")
    os.makedirs("models", exist_ok=True)

    df    = pd.read_csv(INPUT_FILE)
    X     = df[FEATURE_COLS]
    le    = LabelEncoder()
    le.classes_ = np.array(["Low", "Medium", "High"])
    y     = le.transform(df["readiness_label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, class_weight="balanced"))
        ]),
        "decision_tree": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", DecisionTreeClassifier(max_depth=6, min_samples_split=5, random_state=RANDOM_STATE, class_weight="balanced"))
        ]),
        "random_forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_split=4, random_state=RANDOM_STATE, class_weight="balanced", n_jobs=-1))
        ]),
    }

    cv      = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    results = {}

    for name, pipeline in models.items():
        print(f"\n🔧 Training: {name}")
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy")
        pipeline.fit(X_train, y_train)
        test_acc  = pipeline.score(X_test, y_test)
        print(f"   CV: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}  |  Test: {test_acc:.4f}")
        joblib.dump(pipeline, f"models/{name}.pkl")
        print(f"   💾 Saved → models/{name}.pkl")
        results[name] = {"cv_mean": cv_scores.mean(), "test_accuracy": test_acc}

    joblib.dump(le,           "models/label_encoder.pkl")
    joblib.dump(FEATURE_COLS, "models/feature_cols.pkl")
    print("\n💾 Saved label_encoder + feature_cols")

    print("\n" + "="*55)
    best = max(results, key=lambda k: results[k]["test_accuracy"])
    for name, r in results.items():
        print(f"  {name:<25} CV:{r['cv_mean']:.4f}  Test:{r['test_accuracy']:.4f}")
    print(f"\n🏆 Best: {best}")
    return results

if __name__ == "__main__":
    train()