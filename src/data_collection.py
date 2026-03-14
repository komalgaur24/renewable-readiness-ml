"""
Step 1: Data Collection
Primary: Kaggle global-data-on-sustainable-energy.csv
Enrichment: World Bank CSVs for missing columns
"""

import pandas as pd
import numpy as np
import os

KAGGLE_FILE  = "data/raw/global-data-on-sustainable-energy.csv"
GDP_FILE     = "data/raw/gdp_per_capita.csv"
ELEC_FILE    = "data/raw/electricity_access.csv"
RENEW_FILE   = "data/raw/renewable_share.csv"
URBAN_FILE   = "data/raw/urban_population.csv"
OUTPUT_FILE  = "data/raw/world_bank_data.csv"
TARGET_YEAR  = 2019

AGGREGATE_KEYWORDS = [
    "world","income","region","area","union","euro","oecd",
    "africa","asia","europe","america","caribbean","pacific",
    "developing","developed","least","small","island","fragile",
    "sub-saharan","middle east","north africa","central asia",
    "south asia","east asia","latin","heavily indebted"
]


def parse_wb_csv(filepath, col_name):
    """Parse World Bank CSV — skip 4 header rows, get most recent value per country."""
    print(f"   Loading WB: {filepath}")
    df = pd.read_csv(filepath, skiprows=4, encoding="latin1")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df = df.rename(columns={"Country Name": "country_name", "Country Code": "country_code"})

    year_cols = sorted([c for c in df.columns if str(c).strip().isdigit()], reverse=True)

    def get_latest(row):
        for yr in year_cols:
            val = row[yr]
            if pd.notna(val) and val != "":
                try:
                    return float(val)
                except:
                    continue
        return np.nan

    df[col_name] = df.apply(get_latest, axis=1)

    # Remove aggregates
    df = df[~df["country_name"].str.lower().apply(
        lambda x: any(kw in str(x) for kw in AGGREGATE_KEYWORDS)
    )]

    result = df[["country_name", "country_code", col_name]].dropna(subset=["country_code"])
    result = result.drop_duplicates(subset=["country_code"])
    print(f"   → {len(result)} countries for '{col_name}'")
    return result


def load_kaggle():
    """Load Kaggle dataset and extract all available features."""
    print(f"\n📂 Loading Kaggle: {KAGGLE_FILE}")
    df = pd.read_csv(KAGGLE_FILE, encoding="latin1")
    print(f"   Raw shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")

    # Flexible column renaming
    col_map = {}
    for col in df.columns:
        cl = col.lower().strip()
        if cl == "entity":
            col_map[col] = "country_name"
        elif cl == "year":
            col_map[col] = "year"
        elif "gdp_per_capita" in cl:
            col_map[col] = "gdp_per_capita"
        elif "access to electricity" in cl:
            col_map[col] = "electricity_access_pct"
        elif "renewable energy share" in cl:
            col_map[col] = "renewable_share_pct"
        elif "primary energy consumption per capita" in cl:
            col_map[col] = "energy_use_per_capita"
        elif "urban population" in cl:
            col_map[col] = "urban_population_abs"
        elif cl == "population":
            col_map[col] = "population"

    df = df.rename(columns=col_map)

    # Filter to target year
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df_year = df[df["year"] == TARGET_YEAR].copy()
        if len(df_year) < 50:
            best = df.groupby("year")["country_name"].count().idxmax()
            print(f"   ⚠️  {TARGET_YEAR} sparse. Using {best} instead.")
            df_year = df[df["year"] == best].copy()
        else:
            print(f"   ✅ {len(df_year)} countries for year {TARGET_YEAR}")
    else:
        df_year = df.copy()

    # Compute urban % from absolute if available
    if "urban_population_pct" not in df_year.columns:
        if "urban_population_abs" in df_year.columns and "population" in df_year.columns:
            df_year["urban_population_abs"] = pd.to_numeric(df_year["urban_population_abs"], errors="coerce")
            df_year["population"]           = pd.to_numeric(df_year["population"],           errors="coerce")
            df_year["urban_population_pct"] = (
                df_year["urban_population_abs"] / df_year["population"] * 100
            ).clip(0, 100)
            filled = df_year["urban_population_pct"].notna().sum()
            print(f"   ✅ Computed urban_population_pct for {filled} countries")
        else:
            df_year["urban_population_pct"] = np.nan
            print(f"   ⚠️  urban_population_pct not computable — will fill from World Bank")

    df_year = df_year.drop_duplicates(subset=["country_name"])
    return df_year


def collect_all():
    print("\n🌍 Starting Data Collection...\n")
    os.makedirs("data/raw", exist_ok=True)

    # ── Step A: Load Kaggle ────────────────────────────────────
    kaggle = load_kaggle()

    needed_cols = ["country_name",
                   "gdp_per_capita", "electricity_access_pct",
                   "renewable_share_pct", "energy_use_per_capita",
                   "urban_population_pct"]

    for c in needed_cols:
        if c not in kaggle.columns:
            kaggle[c] = np.nan

    base = kaggle[needed_cols].copy()

    # ── Step B: Load World Bank CSVs ──────────────────────────
    print("\n📊 Loading World Bank CSVs for enrichment...")

    wb_urban = parse_wb_csv(URBAN_FILE, "urban_wb")
    wb_gdp   = parse_wb_csv(GDP_FILE,   "gdp_wb")
    wb_elec  = parse_wb_csv(ELEC_FILE,  "elec_wb")
    wb_renew = parse_wb_csv(RENEW_FILE, "renew_wb")

    # Get country_code mapping from WB GDP file
    code_map = wb_gdp[["country_name", "country_code"]].copy()

    # Merge country_code into base
    base = pd.merge(base, code_map, on="country_name", how="left")

    # Merge WB columns by country_code
    for wb_df, wb_col in [
        (wb_urban, "urban_wb"),
        (wb_gdp,   "gdp_wb"),
        (wb_elec,  "elec_wb"),
        (wb_renew, "renew_wb"),
    ]:
        base = pd.merge(base, wb_df[["country_code", wb_col]],
                        on="country_code", how="left")

    # ── Step C: Fill missing Kaggle values from World Bank ─────
    print("\n🔄 Filling missing values from World Bank...")

    fill_map = {
        "urban_population_pct": "urban_wb",
        "gdp_per_capita":       "gdp_wb",
        "electricity_access_pct": "elec_wb",
        "renewable_share_pct":  "renew_wb",
    }
    for kaggle_col, wb_col in fill_map.items():
        before = base[kaggle_col].isna().sum()
        base[kaggle_col] = base[kaggle_col].fillna(base[wb_col])
        after  = base[kaggle_col].isna().sum()
        print(f"   '{kaggle_col}': filled {before - after} missing values (still missing: {after})")

    # ── Step D: Also try merging WB by country name directly ───
    # For countries not matched by code
    for wb_df, wb_col, target_col in [
        (wb_urban, "urban_wb",  "urban_population_pct"),
        (wb_gdp,   "gdp_wb",   "gdp_per_capita"),
        (wb_elec,  "elec_wb",  "electricity_access_pct"),
        (wb_renew, "renew_wb", "renewable_share_pct"),
    ]:
        still_missing = base[target_col].isna()
        if still_missing.sum() > 0:
            name_map = dict(zip(wb_df["country_name"], wb_df[wb_col]))
            base.loc[still_missing, target_col] = base.loc[still_missing, "country_name"].map(name_map)

    # ── Step E: Drop WB helper columns ────────────────────────
    base = base.drop(columns=["urban_wb","gdp_wb","elec_wb","renew_wb"], errors="ignore")

    # ── Step F: Remove non-countries ──────────────────────────
    base = base[~base["country_name"].str.lower().apply(
        lambda x: any(kw in str(x) for kw in AGGREGATE_KEYWORDS)
    )]
    base = base.drop_duplicates(subset=["country_name"])
    base = base.dropna(subset=["country_name"])

    # ── Summary ───────────────────────────────────────────────
    print(f"\n✅ Final dataset: {len(base)} countries")
    print(f"   Columns: {list(base.columns)}")
    print(f"\n   Missing values per column:")
    for col in needed_cols[1:]:
        print(f"   {col:<30}: {base[col].isna().sum()} missing")

    base.to_csv(OUTPUT_FILE, index=False)
    print(f"\n💾 Saved → {OUTPUT_FILE}")
    return base


if __name__ == "__main__":
    df = collect_all()
    print(f"\nPreview:")
    print(df.head(8).to_string())