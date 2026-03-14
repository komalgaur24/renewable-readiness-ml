import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.preprocessing import label_binarize

FEATURE_COLS = joblib.load("models/feature_cols.pkl")
CLASSES      = ["Low", "Medium", "High"]
RANDOM_STATE = 42
os.makedirs("data/plots", exist_ok=True)

def load_test_data():
    df = pd.read_csv("data/raw/labeled_data.csv")
    le = joblib.load("models/label_encoder.pkl")
    X  = df[FEATURE_COLS]
    y  = le.transform(df["readiness_label"])
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    return X_test, y_test

def evaluate():
    print("📊 Evaluating Models...\n")
    X_test, y_test = load_test_data()
    summary = {}

    for name in ["logistic_regression", "decision_tree", "random_forest"]:
        pipeline = joblib.load(f"models/{name}.pkl")
        y_pred   = pipeline.predict(X_test)
        y_prob   = pipeline.predict_proba(X_test)
        y_bin    = label_binarize(y_test, classes=[0,1,2])
        acc      = accuracy_score(y_test, y_pred)
        auc      = roc_auc_score(y_bin, y_prob, multi_class="ovr", average="macro")

        print(f"\n{'='*50}\n  {name}\n{'='*50}")
        print(classification_report(y_test, y_pred, target_names=CLASSES))
        print(f"  AUC-ROC: {auc:.4f}")

        cm  = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots(figsize=(6,5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="YlOrRd",
                    xticklabels=CLASSES, yticklabels=CLASSES, ax=ax)
        ax.set_title(f"Confusion Matrix — {name}")
        ax.set_ylabel("True")
        ax.set_xlabel("Predicted")
        plt.tight_layout()
        plt.savefig(f"data/plots/cm_{name}.png", dpi=150)
        plt.close()
        summary[name] = {"accuracy": acc, "auc": auc}

    # Feature importance
    rf  = joblib.load("models/random_forest.pkl").named_steps["clf"]
    imp = rf.feature_importances_
    idx = np.argsort(imp)
    fig, ax = plt.subplots(figsize=(9,5))
    ax.barh(
        [FEATURE_COLS[i] for i in idx],
        [imp[i] for i in idx],
        color=plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(FEATURE_COLS)))
    )
    ax.set_title("Feature Importance — Random Forest")
    ax.set_xlabel("Importance")
    plt.tight_layout()
    plt.savefig("data/plots/feature_importance.png", dpi=150)
    plt.close()

    # Model comparison
    names = list(summary.keys())
    accs  = [summary[n]["accuracy"] for n in names]
    aucs  = [summary[n]["auc"]      for n in names]
    x     = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8,5))
    b1 = ax.bar(x - 0.2, accs, 0.35, label="Accuracy", color="#2ECC71")
    b2 = ax.bar(x + 0.2, aucs, 0.35, label="AUC-ROC",  color="#3498DB")
    ax.set_xticks(x)
    ax.set_xticklabels([n.replace("_"," ").title() for n in names])
    ax.set_ylim(0, 1.15)
    ax.set_title("Model Comparison")
    ax.legend()
    for bar in list(b1) + list(b2):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("data/plots/model_comparison.png", dpi=150)
    plt.close()

    print("\n✅ All plots saved in data/plots/")
    print("\n📊 FINAL SUMMARY:")
    for n, r in summary.items():
        print(f"  {n:<25} Acc:{r['accuracy']:.4f}  AUC:{r['auc']:.4f}")

if __name__ == "__main__":
    evaluate()