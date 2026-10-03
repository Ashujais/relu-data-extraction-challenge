"""
Master Execution Pipeline
Relu Consultancy Data Extraction Challenge

Orchestrates the entire extraction, cleaning, validation, and analysis
pipeline for both Objective 1 (Disney Cruise) and Objective 2 (Ingredients Network).
Exports all answers to output/analysis_results.json and validates final CSV files.
"""

import os
import sys
import json
import logging
import pandas as pd

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "run_all.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("MasterPipeline")


def validate_csv(path: str, required_cols: list) -> bool:
    """Validate CSV exists, has non-zero rows, and contains required columns."""
    if not os.path.exists(path):
        logger.error(f"Validation FAILED: File does not exist at {path}")
        return False
    df = pd.read_csv(path)
    if df.empty:
        logger.error(f"Validation FAILED: File {path} is empty.")
        return False
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        logger.error(f"Validation FAILED: Missing required columns {missing} in {path}")
        return False
    logger.info(f"Validation PASSED for {path} ({len(df)} records, all required columns present).")
    return True


def run_pipeline():
    logger.info("==================================================")
    logger.info("STARTING RELU CONSULTANCY MASTER PIPELINE")
    logger.info("==================================================")

    # 1. Disney Cruise Pipeline
    logger.info("\n--- [1/2] EXECUTING OBJECTIVE 1: DISNEY CRUISE ---")
    try:
        from disney_cruise.disney_cruise_scraper import DisneyCruiseScraper
        from disney_cruise.disney_cruise_cleaner import clean_disney_data
        from disney_cruise.disney_cruise_analysis import analyze_disney_data

        if not os.path.exists(os.path.join("output", "disney_cruises_raw.csv")):
            logger.info("Running Disney Cruise Scraper...")
            scraper = DisneyCruiseScraper()
            scraper.run()

        logger.info("Running Disney Cruise Data Cleaner...")
        clean_disney_data()

        logger.info("Running Disney Cruise Analysis...")
        disney_results = analyze_disney_data()

    except Exception as e:
        logger.error(f"Error in Disney Cruise pipeline: {e}")
        disney_results = {}

    # 2. Ingredients Network Pipeline
    logger.info("\n--- [2/2] EXECUTING OBJECTIVE 2: INGREDIENTS NETWORK ---")
    try:
        from ingredients_network.ingredients_network_scraper import IngredientsNetworkScraper
        from ingredients_network.ingredients_network_cleaner import clean_ingredients_data
        from ingredients_network.ingredients_network_analysis import analyze_ingredients_data

        if not os.path.exists(os.path.join("output", "ingredients_network_raw.csv")):
            logger.info("Running Ingredients Network Scraper...")
            scraper = IngredientsNetworkScraper()
            scraper.run(max_records=500)

        logger.info("Running Ingredients Network Data Cleaner...")
        clean_ingredients_data()

        logger.info("Running Ingredients Network Analysis...")
        ingredients_results = analyze_ingredients_data()

    except Exception as e:
        logger.error(f"Error in Ingredients Network pipeline: {e}")
        ingredients_results = {}

    # 3. CSV Validations
    logger.info("\n--- [3/3] RUNNING AUTOMATED DATA VALIDATIONS ---")
    disney_ok = validate_csv(
        os.path.join("output", "disney_cruises.csv"),
        ["cruise_title", "ship", "destination", "departure_port", "number_of_booking_dates"]
    )
    ingredients_ok = validate_csv(
        os.path.join("output", "ingredients_network.csv"),
        ["company_name", "primary_business_activity", "address", "website"]
    )

    # 4. Save Final Analysis JSON
    final_output = {
        "disney_cruise_analysis": disney_results,
        "ingredients_network_analysis": ingredients_results,
        "validation_status": {
            "disney_csv_valid": disney_ok,
            "ingredients_csv_valid": ingredients_ok,
        }
    }
    
    analysis_json_path = os.path.join("output", "analysis_results.json")
    with open(analysis_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)
    logger.info(f"\nFinal analysis results saved to {analysis_json_path}")

    logger.info("==================================================")
    logger.info("MASTER PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("==================================================")


if __name__ == "__main__":
    run_pipeline()
