import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
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

    df = pd.read_csv(INPUT_FILE)
    X  = df[FEATURE_COLS]
    le = LabelEncoder()
    le.classes_ = np.array(["Low", "Medium", "High"])
    y  = le.transform(df["readiness_label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2,
        random_state=RANDOM_STATE, stratify=y
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                max_iter=2000,
                random_state=RANDOM_STATE,
                class_weight="balanced",
                C=10,
                solver="lbfgs",
            ))
        ]),
        "decision_tree": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", DecisionTreeClassifier(
                max_depth=4,
                min_samples_split=8,
                min_samples_leaf=4,
                random_state=RANDOM_STATE,
                class_weight="balanced",
                criterion="entropy",
            ))
        ]),
        "random_forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=500,
                max_depth=6,
                min_samples_split=6,
                min_samples_leaf=3,
                max_features="sqrt",
                random_state=RANDOM_STATE,
                class_weight="balanced",
                n_jobs=-1,
                bootstrap=True,
                oob_score=True,
            ))
        ]),
        "gradient_boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                min_samples_split=6,
                min_samples_leaf=3,
                random_state=RANDOM_STATE,
                subsample=0.8,
            ))
        ]),
        "svm": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(
                kernel="rbf",
                C=10,
                gamma="scale",
                probability=True,
                random_state=RANDOM_STATE,
                class_weight="balanced",
            ))
        ]),
    }

    cv      = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    results = {}

    for name, pipeline in models.items():
        print(f"\n🔧 Training: {name}")
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy")
        pipeline.fit(X_train, y_train)
        test_acc = pipeline.score(X_test, y_test)
        print(f"   CV:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"   Test: {test_acc:.4f}")
        joblib.dump(pipeline, f"models/{name}.pkl")
        print(f"   💾 Saved → models/{name}.pkl")
        results[name] = {
            "cv_mean": cv_scores.mean(),
            "cv_std":  cv_scores.std(),
            "test_accuracy": test_acc,
        }

    joblib.dump(le,           "models/label_encoder.pkl")
    joblib.dump(FEATURE_COLS, "models/feature_cols.pkl")
    print("\n💾 Saved label_encoder + feature_cols")

    print("\n" + "="*55)
    print("📊 TRAINING SUMMARY")
    print("="*55)
    for name, r in results.items():
        print(f"  {name:<25} CV:{r['cv_mean']*100:.1f}%  Test:{r['test_accuracy']*100:.1f}%")

    best = max(results, key=lambda k: results[k]["test_accuracy"])
    print(f"\n🏆 Best Model: {best} ({results[best]['test_accuracy']*100:.1f}%)")
    return results

if __name__ == "__main__":
    train()