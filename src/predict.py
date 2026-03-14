import pandas as pd
import numpy as np
import joblib
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import label_binarize

load_dotenv()
FEATURE_COLS = joblib.load("models/feature_cols.pkl")
MONGO_URI    = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB     = os.getenv("MONGO_DB",  "renewable_readiness")

def predict_all():
    print("🔮 Generating predictions...\n")
    df       = pd.read_csv("data/raw/labeled_data.csv")
    pipeline = joblib.load("models/logistic_regression.pkl")
    le       = joblib.load("models/label_encoder.pkl")

    X      = df[FEATURE_COLS]
    y_pred = pipeline.predict(X)
    y_prob = pipeline.predict_proba(X)

    df["predicted_label"]       = le.inverse_transform(y_pred)
    df["prob_low"]              = y_prob[:,0].round(3)
    df["prob_medium"]           = y_prob[:,1].round(3)
    df["prob_high"]             = y_prob[:,2].round(3)
    df["prediction_confidence"] = y_prob.max(axis=1).round(3)

    out_cols = ["country_name", "readiness_score", "readiness_label",
                "predicted_label", "prob_low", "prob_medium", "prob_high",
                "prediction_confidence"] + FEATURE_COLS
    if "country_code" in df.columns:
        out_cols = ["country_code"] + out_cols

    out = df[out_cols].sort_values("readiness_score", ascending=False)
    out.to_csv("data/raw/predictions.csv", index=False)
    print(f"✅ Predictions saved — {len(out)} countries")
    print(f"\nTop 5:")
    print(out[["country_name","readiness_score","predicted_label"]].head().to_string(index=False))

    push_to_mongodb(df, out)
    return out

def push_to_mongodb(df, out):
    print(f"\n🍃 Pushing to MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[MONGO_DB]

        db["countries"].drop()
        db["countries"].insert_many(out.to_dict(orient="records"))
        print(f"   ✅ {len(out)} countries inserted")

        le2 = joblib.load("models/label_encoder.pkl")
        X   = df[FEATURE_COLS]
        y   = le2.transform(df["readiness_label"])
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        db["model_metrics"].drop()
        for model_name in ["logistic_regression", "decision_tree", "random_forest"]:
            pipe   = joblib.load(f"models/{model_name}.pkl")
            y_pred = pipe.predict(X_test)
            y_prob = pipe.predict_proba(X_test)
            y_bin  = label_binarize(y_test, classes=[0,1,2])
            acc    = accuracy_score(y_test, y_pred)
            auc    = roc_auc_score(y_bin, y_prob, multi_class="ovr", average="macro")
            db["model_metrics"].insert_one({
                "model":    model_name,
                "accuracy": round(acc, 4),
                "auc_roc":  round(auc, 4),
            })
        print(f"   ✅ Model metrics inserted")

        db["feature_stats"].drop()
        db["feature_stats"].insert_one({"stats": df[FEATURE_COLS].describe().to_dict()})
        print(f"   ✅ Feature stats inserted")

        client.close()
        print(f"\n🍃 MongoDB complete! DB: {MONGO_DB}")

    except Exception as e:
        print(f"   ⚠️  MongoDB error: {e} — CSV still works fine")

if __name__ == "__main__":
    predict_all()