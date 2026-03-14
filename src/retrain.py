"""
Level 2 Auto-Retraining System
- Checks MongoDB for logged predictions
- Combines with original training data
- Retrains model when threshold reached
- Saves updated .pkl files
"""

import pandas as pd
import numpy as np
import joblib
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import label_binarize
from datetime import datetime

load_dotenv()

MONGO_URI    = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB     = os.getenv("MONGO_DB",  "renewable_readiness")
RETRAIN_THRESHOLD = 50  # retrain after this many new predictions
RANDOM_STATE = 42

FEATURE_COLS = [
    "log_gdp_per_capita",
    "urban_population_pct",
    "log_energy_use_per_capita",
    "electricity_access_pct",
    "renewable_share_pct",
    "energy_pressure_index",
    "infrastructure_score",
]


def get_log_count():
    """Check how many predictions are logged in MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db     = client[MONGO_DB]
        count  = db["predictions_log"].count_documents({})
        client.close()
        return count
    except Exception as e:
        print(f"   ⚠️  MongoDB error: {e}")
        return 0


def get_logged_predictions():
    """Pull all logged predictions from MongoDB."""
    try:
        client  = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db      = client[MONGO_DB]
        records = list(db["predictions_log"].find({}, {"_id": 0}))
        client.close()
        return pd.DataFrame(records) if records else pd.DataFrame()
    except Exception as e:
        print(f"   ⚠️  MongoDB error: {e}")
        return pd.DataFrame()


def prepare_logged_data(logs_df):
    """
    Convert raw logged predictions into feature format
    matching the original training data structure.
    """
    if logs_df.empty:
        return pd.DataFrame()

    print(f"   Processing {len(logs_df)} logged predictions...")

    prepared = pd.DataFrame()

    # Reconstruct features from raw inputs
    prepared["log_gdp_per_capita"]        = np.log1p(logs_df["gdp"])
    prepared["urban_population_pct"]      = logs_df["urban"]
    prepared["log_energy_use_per_capita"] = np.log1p(logs_df["energy"])
    prepared["electricity_access_pct"]    = logs_df["electricity"]
    prepared["renewable_share_pct"]       = logs_df["renewable"]

    # Recompute engineered features
    max_energy = logs_df["energy"].max()
    prepared["energy_pressure_index"] = (
        (logs_df["energy"] / (max_energy + 1e-9)) *
        (1 - logs_df["renewable"] / 100)
    ).values

    prepared["infrastructure_score"] = (
        (logs_df["electricity"] + logs_df["urban"]) / 2
    ).values

    # Use predicted_label as the target
    prepared["readiness_label"] = logs_df["predicted_label"].values

    print(f"   ✅ Prepared {len(prepared)} logged samples")
    return prepared


def load_original_data():
    """Load original labeled training data."""
    df = pd.read_csv("data/raw/labeled_data.csv")
    print(f"   ✅ Original data: {len(df)} countries")
    return df[FEATURE_COLS + ["readiness_label"]]


def combine_datasets(original_df, logged_df):
    """
    Combine original data with logged predictions.
    Original data weighted more heavily (duplicated 3x).
    """
    if logged_df.empty:
        return original_df

    # Weight original data 3x to maintain quality
    original_weighted = pd.concat([original_df] * 3, ignore_index=True)

    combined = pd.concat(
        [original_weighted, logged_df[FEATURE_COLS + ["readiness_label"]]],
        ignore_index=True
    )
    combined = combined.dropna()

    print(f"   ✅ Combined dataset: {len(combined)} samples")
    print(f"      Original (3x): {len(original_weighted)}")
    print(f"      New logs:      {len(logged_df)}")
    return combined


def retrain_models(combined_df):
    """Retrain all 3 models on combined dataset."""
    print("\n🤖 Retraining models on combined dataset...")

    le = LabelEncoder()
    le.classes_ = np.array(["Low", "Medium", "High"])

    X = combined_df[FEATURE_COLS]
    y = le.transform(combined_df["readiness_label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                max_iter=1000,
                random_state=RANDOM_STATE,
                class_weight="balanced"
            ))
        ]),
        "decision_tree": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", DecisionTreeClassifier(
                max_depth=6,
                min_samples_split=5,
                random_state=RANDOM_STATE,
                class_weight="balanced"
            ))
        ]),
        "random_forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=200,
                max_depth=8,
                min_samples_split=4,
                random_state=RANDOM_STATE,
                class_weight="balanced",
                n_jobs=-1
            ))
        ]),
    }

    cv      = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    results = {}

    for name, pipeline in models.items():
        print(f"\n   🔧 Training: {name}")
        cv_scores = cross_val_score(
            pipeline, X_train, y_train,
            cv=cv, scoring="accuracy"
        )
        pipeline.fit(X_train, y_train)
        y_pred   = pipeline.predict(X_test)
        y_prob   = pipeline.predict_proba(X_test)
        y_bin    = label_binarize(y_test, classes=[0, 1, 2])
        test_acc = accuracy_score(y_test, y_pred)
        auc      = roc_auc_score(
            y_bin, y_prob,
            multi_class="ovr", average="macro"
        )

        print(f"      CV:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"      Test: {test_acc:.4f}  AUC: {auc:.4f}")

        # Save updated model
        joblib.dump(pipeline, f"models/{name}.pkl")
        print(f"      💾 Saved → models/{name}.pkl")

        results[name] = {
            "model":    name,
            "accuracy": round(test_acc, 4),
            "auc_roc":  round(auc, 4),
        }

    # Save label encoder and feature cols
    joblib.dump(le,           "models/label_encoder.pkl")
    joblib.dump(FEATURE_COLS, "models/feature_cols.pkl")

    return results


def update_mongodb_metrics(results):
    """Push updated model metrics to MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db     = client[MONGO_DB]

        db["model_metrics"].drop()
        for r in results.values():
            db["model_metrics"].insert_one(r)

        # Log retrain event
        db["retrain_log"].insert_one({
            "timestamp":    datetime.now().isoformat(),
            "trigger":      "threshold_reached",
            "samples_used": "original_3x + logged",
            "best_model":   max(results, key=lambda k: results[k]["accuracy"]),
            "best_accuracy": max(r["accuracy"] for r in results.values()),
        })

        client.close()
        print("\n   ✅ MongoDB metrics updated")

    except Exception as e:
        print(f"   ⚠️  MongoDB error: {e}")


def archive_used_logs():
    """Move used logs to archive collection so they aren't reused."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db     = client[MONGO_DB]

        logs = list(db["predictions_log"].find({}, {"_id": 0}))
        if logs:
            db["predictions_log_archive"].insert_many(logs)
            db["predictions_log"].drop()
            print(f"   ✅ Archived {len(logs)} used logs")

        client.close()

    except Exception as e:
        print(f"   ⚠️  Archive error: {e}")


def check_and_retrain(force=False):
    """
    Main function:
    - Check log count
    - If >= threshold → retrain
    - force=True → retrain regardless of count
    """
    print("\n🔍 Checking retrain status...\n")

    count = get_log_count()
    print(f"   Logged predictions: {count} / {RETRAIN_THRESHOLD}")

    if not force and count < RETRAIN_THRESHOLD:
        remaining = RETRAIN_THRESHOLD - count
        print(f"   ℹ️  Need {remaining} more predictions before retraining")
        print(f"   ✅ Current model is still active — no retrain needed")
        return False

    print(f"\n🚀 {'Force retrain triggered!' if force else 'Threshold reached!'}")
    print("   Starting retraining pipeline...\n")

    # Step 1: Load original data
    print("📂 Step 1: Loading original data...")
    original_df = load_original_data()

    # Step 2: Get logged predictions
    print("\n📊 Step 2: Loading logged predictions...")
    logs_df  = get_logged_predictions()
    prepared = prepare_logged_data(logs_df)

    # Step 3: Combine datasets
    print("\n🔗 Step 3: Combining datasets...")
    combined = combine_datasets(original_df, prepared)

    # Step 4: Retrain models
    results = retrain_models(combined)

    # Step 5: Update MongoDB
    print("\n🍃 Step 5: Updating MongoDB metrics...")
    update_mongodb_metrics(results)

    # Step 6: Archive used logs
    print("\n📦 Step 6: Archiving used logs...")
    archive_used_logs()

    print("\n" + "="*55)
    print("✅ RETRAINING COMPLETE!")
    print("="*55)
    best = max(results, key=lambda k: results[k]["accuracy"])
    for name, r in results.items():
        print(f"  {name:<25} Acc:{r['accuracy']:.4f}  AUC:{r['auc_roc']:.4f}")
    print(f"\n🏆 Best Model: {best} ({results[best]['accuracy']:.4f})")
    print(f"💾 All models updated in models/ folder")
    print(f"🍃 MongoDB metrics updated")
    print("="*55)
    return True


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    check_and_retrain(force=force)