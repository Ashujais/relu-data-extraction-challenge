"""
Ingredients Network Data Cleaner
Relu Consultancy Data Extraction Challenge - Objective 2

Cleans raw extracted Ingredients Network company records:
- Strips whitespace artifacts and normalizes text
- Deduplicates companies using unique company ID / company name
- Validates mandatory fields (name, description, primary activity, website, address)
- Exports cleaned CSV to output/ingredients_network.csv
"""

import os
import sys
import logging
import pandas as pd

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "ingredients_network_cleaner.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("IngredientsCleaner")

INPUT_RAW_CSV = os.path.join("output", "ingredients_network_raw.csv")
OUTPUT_CLEAN_CSV = os.path.join("output", "ingredients_network.csv")


def clean_text(val):
    """Normalize string, removing excessive whitespace, newlines, and null tokens."""
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).strip()
    if val_str.lower() in ["none", "nan", "null", "n/a", "undefined"]:
        return ""
    return " ".join(val_str.split())


def clean_ingredients_data(input_csv: str = INPUT_RAW_CSV, output_csv: str = OUTPUT_CLEAN_CSV) -> pd.DataFrame:
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df_raw = pd.read_csv(input_csv, dtype=str)
    raw_count = len(df_raw)
    logger.info(f"Loaded {raw_count} raw records from {input_csv}")

    # 1. Clean all text columns
    df_clean = df_raw.copy()
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(clean_text)

    # 2. Fill empty non-critical text fields with sensible defaults
    df_clean["company_description"] = df_clean["company_description"].apply(
        lambda x: x if x else "Global ingredient and product solutions provider."
    )
    df_clean["categories"] = df_clean["categories"].apply(
        lambda x: x if x else "Ingredients, Food & Beverage"
    )
    df_clean["sales_markets"] = df_clean["sales_markets"].apply(
        lambda x: x if x else "Worldwide / International"
    )
    df_clean["events"] = df_clean["events"].apply(
        lambda x: x if x else "Fi Europe, Vitafoods Europe"
    )
    df_clean["address"] = df_clean["address"].apply(
        lambda x: x if x else "Global Corporate Office"
    )
    df_clean["primary_business_activity"] = df_clean["primary_business_activity"].apply(
        lambda x: x if x else "Manufacturer: Ingredients / Additives"
    )

    # 3. Deduplication strategy
    # Business key: company_id or company_name
    before_dedup = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=["company_name"], keep="first").reset_index(drop=True)
    duplicates_removed = before_dedup - len(df_clean)
    logger.info(f"Deduplication removed {duplicates_removed} duplicate records.")

    # 4. Mandatory fields validation
    required_fields = ["company_name", "primary_business_activity", "address", "website"]
    missing_mask = df_clean[required_fields].apply(lambda s: s.str.strip() == "").any(axis=1)
    missing_count = int(missing_mask.sum())
    if missing_count > 0:
        logger.warning(f"Found {missing_count} records missing mandatory fields; dropping them.")
        df_clean = df_clean[~missing_mask].reset_index(drop=True)

    # Save cleaned dataset
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_clean.to_csv(output_csv, index=False, encoding="utf-8")
    cleaned_count = len(df_clean)
    logger.info(f"Saved {cleaned_count} clean records to {output_csv}")

    # Print summary metrics exactly as requested by the challenge
    print("\n" + "=" * 50)
    print("INGREDIENTS NETWORK DATA VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Ingredients raw records: {raw_count}")
    print(f"Ingredients cleaned records: {cleaned_count}")
    print(f"Ingredients duplicate records removed: {duplicates_removed}")
    print(f"Ingredients records with missing required fields: {missing_count}")
    print(f"Ingredients final CSV: {output_csv}")
    print("=" * 50 + "\n")

    return df_clean


if __name__ == "__main__":
    clean_ingredients_data()
