"""
Step 2: Preprocessing
- Remove non-country rows
- Handle missing values
- Validate ranges
- Save cleaned data
"""

import pandas as pd
import numpy as np

INPUT_FILE  = "data/raw/world_bank_data.csv"
OUTPUT_FILE = "data/raw/cleaned_data.csv"

FEATURE_COLS = [
    "gdp_per_capita",
    "urban_population_pct",
    "energy_use_per_capita",
    "electricity_access_pct",
    "renewable_share_pct",
]

AGGREGATE_KEYWORDS = [
    "world","income","region","area","union","euro","oecd",
    "africa","asia","europe","america","caribbean","pacific",
    "developing","developed","least","small","island","fragile",
    "sub-saharan","middle east","north africa","central asia",
    "south asia","east asia","latin","heavily indebted"
]


def load(path=INPUT_FILE):
    df = pd.read_csv(path)
    print(f"📂 Loaded: {df.shape[0]} rows × {df.shape[1]} cols")
    return df


def remove_non_countries(df):
    before = len(df)
    mask = df["country_name"].str.lower().apply(
        lambda x: not any(kw in str(x) for kw in AGGREGATE_KEYWORDS)
    )
    df = df[mask]
    print(f"🗑️  Removed {before - len(df)} non-country rows → {len(df)} remain")
    return df


def ensure_feature_cols(df):
    """Add missing feature columns as NaN so pipeline doesn't break."""
    for col in FEATURE_COLS:
        if col not in df.columns:
            df[col] = np.nan
            print(f"   ⚠️  Added missing column '{col}' as NaN")
    return df


def drop_high_missing(df, threshold=0.5):
    before = len(df)
    available = [c for c in FEATURE_COLS if c in df.columns]
    df = df.dropna(thresh=int((1 - threshold) * len(available)) + 1,
                   subset=available)
    print(f"🗑️  Dropped {before - len(df)} rows with >{int(threshold*100)}% missing → {len(df)} remain")
    return df


def impute_median(df):
    for col in FEATURE_COLS:
        if col in df.columns:
            n = df[col].isna().sum()
            if n > 0:
                med = df[col].median()
                df[col] = df[col].fillna(med)
                print(f"   Imputed {n} NaNs in '{col}' → median={med:.2f}")
    return df


def clip_ranges(df):
    pct_cols = ["urban_population_pct", "electricity_access_pct", "renewable_share_pct"]
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].clip(0, 100)
    if "gdp_per_capita" in df.columns:
        df["gdp_per_capita"] = df["gdp_per_capita"].clip(0, None)
    if "energy_use_per_capita" in df.columns:
        df["energy_use_per_capita"] = df["energy_use_per_capita"].clip(0, None)
    print("✅ Clipped values to valid ranges")
    return df


def validate(df):
    available = [c for c in FEATURE_COLS if c in df.columns]
    missing_total = df[available].isna().sum().sum()
    assert missing_total == 0, f"Still has {missing_total} missing values!"
    assert len(df) >= 50, f"Too few countries: {len(df)}"
    print(f"✅ Validation passed: {len(df)} countries, 0 missing values")


def preprocess():
    df = load()
    df = remove_non_countries(df)
    df = ensure_feature_cols(df)
    df = drop_high_missing(df)
    df = impute_median(df)
    df = clip_ranges(df)
    validate(df)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n💾 Saved cleaned data → {OUTPUT_FILE}")
    return df


if __name__ == "__main__":
    df = preprocess()
    print(f"\nShape: {df.shape}")
    print(df[["country_name"] + FEATURE_COLS].head(8).to_string())