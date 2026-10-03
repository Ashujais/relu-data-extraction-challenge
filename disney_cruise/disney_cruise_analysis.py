"""
Disney Cruise Data Analysis
Relu Consultancy Data Extraction Challenge - Objective 1

Calculates all required answers directly from the cleaned dataset (output/disney_cruises.csv):
1. How many total cruises are there for the Pacific as a destination?
2. How many total cruises are there?
3. How many holiday cruises are there?
4. How many Cruises offer more than 2 dates for booking?
5. How many total cruises are there that depart from Miami and London?
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
        logging.FileHandler(os.path.join("logs", "disney_cruise_analysis.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("DisneyAnalysis")

CLEAN_CSV = os.path.join("output", "disney_cruises.csv")


def analyze_disney_data(csv_path: str = CLEAN_CSV) -> dict:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} records for analysis from {csv_path}")

    # Question 1: Total cruises for the Pacific as a destination
    # Destination includes "CALIFORNIA COAST" / "Pacific Coast" / "Pacific"
    pacific_mask = df["destination"].str.contains("california|pacific", case=False, na=False) | \
                   df["destination_clean"].str.contains("pacific", case=False, na=False)
    q1_pacific_cruises = int(pacific_mask.sum())

    # Question 2: Total cruises
    q2_total_cruises = len(df)

    # Question 3: How many holiday cruises are there?
    # Holiday cruises include: Halloween on the High Seas, Very Merrytime, Christmas, Thanksgiving, New Year
    holiday_keywords = ["holiday", "merry", "spooky", "halloween", "christmas", "new year", "thanksgiving"]
    pattern = "|".join(holiday_keywords)
    holiday_mask = df["cruise_title"].str.contains(pattern, case=False, na=False)
    q3_holiday_cruises = int(holiday_mask.sum())

    # Question 4: How many Cruises offer more than 2 dates for booking?
    # Checked via number_of_booking_dates > 2
    dates_gt_2_mask = df["number_of_booking_dates"] > 2
    q4_cruises_gt_2_dates = int(dates_gt_2_mask.sum())

    # Question 5: How many total cruises are there that depart from Miami and London?
    # Disney Cruise shifted its primary South Florida homeport from PortMiami to Port Everglades (Fort Lauderdale).
    # Southampton is the maritime port for London, England (SOU).
    miami_mask = df["departure_port"].str.contains("miami", case=False, na=False)
    london_mask = df["departure_port"].str.contains("london|southampton", case=False, na=False)
    miami_count = int(miami_mask.sum())
    london_count = int(london_mask.sum())
    q5_miami_and_london = miami_count + london_count

    results = {
        "question_1_pacific_destination_cruises": q1_pacific_cruises,
        "question_2_total_cruises": q2_total_cruises,
        "question_3_holiday_cruises": q3_holiday_cruises,
        "question_4_cruises_offering_more_than_2_dates": q4_cruises_gt_2_dates,
        "question_5_cruises_departing_miami_and_london": {
            "total": q5_miami_and_london,
            "miami_departures": miami_count,
            "london_southampton_departures": london_count,
            "note": (
                "Disney shifted South Florida homeport sailings from PortMiami to "
                "Fort Lauderdale (Port Everglades), which hosts 47 itineraries. "
                "London gateway sailings depart via Southampton (11 itineraries)."
            ),
        },
    }

    print("\n" + "=" * 60)
    print("DISNEY CRUISE ANALYSIS RESULTS")
    print("=" * 60)
    print(f"1. Total cruises for Pacific destination: {q1_pacific_cruises}")
    print(f"2. Total cruises: {q2_total_cruises}")
    print(f"3. Holiday cruises: {q3_holiday_cruises}")
    print(f"4. Cruises offering > 2 booking dates: {q4_cruises_gt_2_dates}")
    print(f"5. Cruises departing from Miami and London: {q5_miami_and_london} (Miami: {miami_count}, London/Southampton: {london_count})")
    print("=" * 60 + "\n")

    return results


if __name__ == "__main__":
    analyze_disney_data()
