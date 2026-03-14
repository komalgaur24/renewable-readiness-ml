import pandas as pd
import numpy as np

INPUT_FILE   = "data/raw/cleaned_data.csv"
OUTPUT_FILE  = "data/raw/features.csv"

FINAL_FEATURES = [
    "log_gdp_per_capita",
    "urban_population_pct",
    "log_energy_use_per_capita",
    "electricity_access_pct",
    "renewable_share_pct",
    "energy_pressure_index",
    "infrastructure_score",
]

def engineer_features():
    print("🔧 Engineering features...\n")
    df = pd.read_csv(INPUT_FILE)

    df["log_gdp_per_capita"]        = np.log1p(df["gdp_per_capita"])
    df["log_energy_use_per_capita"] = np.log1p(df["energy_use_per_capita"])
    print("   ✅ Log-transformed: gdp_per_capita, energy_use_per_capita")

    max_energy = df["energy_use_per_capita"].max()
    df["energy_pressure_index"] = (
        (df["energy_use_per_capita"] / (max_energy + 1e-9)) *
        (1 - df["renewable_share_pct"] / 100)
    ).round(4)
    print("   ✅ Created: energy_pressure_index")

    df["infrastructure_score"] = (
        (df["electricity_access_pct"] + df["urban_population_pct"]) / 2
    ).round(4)
    print("   ✅ Created: infrastructure_score")

    missing = [f for f in FINAL_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    print(f"\n✅ Feature engineering complete — {len(df)} countries")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"   💾 Saved → {OUTPUT_FILE}")
    return df, FINAL_FEATURES

if __name__ == "__main__":
    df, features = engineer_features()
    print(df[["country_name"] + features].head(8).to_string())