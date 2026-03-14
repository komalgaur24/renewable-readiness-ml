import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

INPUT_FILE  = "data/raw/features.csv"
OUTPUT_FILE = "data/raw/labeled_data.csv"

def compute_readiness_score(df):
    scaler = MinMaxScaler()
    gdp_norm      = scaler.fit_transform(df[["log_gdp_per_capita"]]).flatten()
    infra_norm    = scaler.fit_transform(df[["infrastructure_score"]]).flatten()
    renew_norm    = scaler.fit_transform(df[["renewable_share_pct"]]).flatten()
    pressure_norm = scaler.fit_transform(df[["energy_pressure_index"]]).flatten()

    df["readiness_score"] = (
        0.30 * gdp_norm      * 100 +
        0.30 * infra_norm    * 100 +
        0.25 * renew_norm    * 100 +
        0.15 * (1 - pressure_norm) * 100
    ).round(2)

    print(f"✅ Scores — Min:{df['readiness_score'].min():.1f} Max:{df['readiness_score'].max():.1f} Mean:{df['readiness_score'].mean():.1f}")
    return df

def assign_labels(df):
    # Use percentile-based thresholds for balanced classes
    p33 = df["readiness_score"].quantile(0.33)
    p66 = df["readiness_score"].quantile(0.66)
    print(f"   Thresholds — Low:<{p33:.1f}  Medium:{p33:.1f}-{p66:.1f}  High:>{p66:.1f}")

    def to_label(s):
        if s >= p66:  return "High"
        elif s >= p33: return "Medium"
        else:          return "Low"

    df["readiness_label"] = df["readiness_score"].apply(to_label)
    dist  = df["readiness_label"].value_counts()
    total = len(df)
    print(f"\n📊 Labels — High:{dist.get('High',0)} Medium:{dist.get('Medium',0)} Low:{dist.get('Low',0)}")
    return df

def create_labels():
    df = pd.read_csv(INPUT_FILE)
    df = compute_readiness_score(df)
    df = assign_labels(df)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n💾 Saved → {OUTPUT_FILE}")
    print("\n🏆 Top 10:")
    print(df.nlargest(10,"readiness_score")[["country_name","readiness_score","readiness_label"]].to_string(index=False))
    print("\n📉 Bottom 10:")
    print(df.nsmallest(10,"readiness_score")[["country_name","readiness_score","readiness_label"]].to_string(index=False))
    return df

if __name__ == "__main__":
    create_labels()