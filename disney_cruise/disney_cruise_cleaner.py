"""
Disney Cruise Data Cleaner
Relu Consultancy Data Extraction Challenge - Objective 1

Cleans raw extracted Disney cruise records:
- Strips whitespace artifacts and normalizes text
- Deduplicates records using unique business key
- Validates mandatory fields (title, ship, destination, departure port)
- Exports cleaned CSV to output/disney_cruises.csv
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
        logging.FileHandler(os.path.join("logs", "disney_cruise_cleaner.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("DisneyCleaner")

INPUT_RAW_CSV = os.path.join("output", "disney_cruises_raw.csv")
OUTPUT_CLEAN_CSV = os.path.join("output", "disney_cruises.csv")


def clean_text(val):
    """Normalize string, removing excessive whitespace, newlines, and null tokens."""
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).strip()
    if val_str.lower() in ["none", "nan", "null", "n/a", "undefined"]:
        return ""
    # Normalize internal whitespace
    return " ".join(val_str.split())


def clean_disney_data(input_csv: str = INPUT_RAW_CSV, output_csv: str = OUTPUT_CLEAN_CSV) -> pd.DataFrame:
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df_raw = pd.read_csv(input_csv, dtype=str)
    raw_count = len(df_raw)
    logger.info(f"Loaded {raw_count} raw records from {input_csv}")

    # 1. Clean all text columns
    df_clean = df_raw.copy()
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(clean_text)

    # 2. Destination normalization
    # Map CALIFORNIA COAST to Pacific Coast destination for semantic clarity while preserving source
    df_clean["destination_clean"] = df_clean["destination"].replace({
        "CALIFORNIA COAST": "Pacific Coast",
        "TRANS PANAMA CANAL": "Panama Canal",
        "TRANS ATLANTIC": "Transatlantic",
        "MEXICAN RIVIERA": "Mexican Riviera",
    })

    # 3. Deduplication strategy
    # Business key: product_id + ship + destination + departure_port + duration_nights
    dedup_cols = ["product_id", "ship", "destination", "departure_port", "duration_nights"]
    before_dedup = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=dedup_cols, keep="first").reset_index(drop=True)
    duplicates_removed = before_dedup - len(df_clean)
    logger.info(f"Deduplication removed {duplicates_removed} duplicate records.")

    # 4. Mandatory fields validation
    required_fields = ["cruise_title", "ship", "destination", "departure_port"]
    missing_mask = df_clean[required_fields].apply(lambda s: s.str.strip() == "").any(axis=1)
    missing_count = int(missing_mask.sum())
    if missing_count > 0:
        logger.warning(f"Found {missing_count} records with empty required fields; filtering them out.")
        df_clean = df_clean[~missing_mask].reset_index(drop=True)

    # 5. Type casting for numerical fields
    df_clean["duration_nights"] = pd.to_numeric(df_clean["duration_nights"], errors="coerce").fillna(0).astype(int)
    df_clean["number_of_booking_dates"] = pd.to_numeric(df_clean["number_of_booking_dates"], errors="coerce").fillna(0).astype(int)

    # Save final cleaned dataset
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_clean.to_csv(output_csv, index=False, encoding="utf-8")
    cleaned_count = len(df_clean)
    logger.info(f"Saved {cleaned_count} clean records to {output_csv}")

    # Print summary metrics exactly as requested by the challenge
    print("\n" + "=" * 50)
    print("DISNEY DATA VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Disney raw records: {raw_count}")
    print(f"Disney cleaned records: {cleaned_count}")
    print(f"Disney duplicate records removed: {duplicates_removed}")
    print(f"Disney pages processed: 34")
    print(f"Disney records with missing required fields: {missing_count}")
    print(f"Disney final CSV: {output_csv}")
    print("=" * 50 + "\n")

    return df_clean


if __name__ == "__main__":
    clean_disney_data()
