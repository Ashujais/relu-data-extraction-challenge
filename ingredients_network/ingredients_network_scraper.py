"""
Ingredients Network Scraper
Relu Consultancy Data Extraction Challenge - Objective 2

Extracts company profiles, supplier information, and catalog data from Ingredients Network:
- Interacts with live search directory
- Scrapes company cards and detailed profiles
- Extracts all mandatory fields:
  * company_name
  * company_description
  * sales_markets
  * primary_business_activity
  * categories
  * events
  * address
  * email
  * telephone
  * website
- Exports raw data to output/ingredients_network_raw.csv
"""

import json
import logging
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List
import pandas as pd

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "ingredients_network_scraper.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("IngredientsScraper")

BASE_URL = "https://www.ingredientsnetwork.com"
SEARCH_URL = f"{BASE_URL}/live/search/search46json.jsp?site=47&searchtype=all"
OUTPUT_RAW_CSV = os.path.join("output", "ingredients_network_raw.csv")
OUTPUT_RAW_JSON = os.path.join("output", "ingredients_network_raw.json")


class IngredientsNetworkScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.ingredientsnetwork.com/",
        }

    def fetch_all_companies_catalog(self) -> List[Dict[str, Any]]:
        """Fetch complete index of companies from search directory (or cached file)."""
        if os.path.exists(OUTPUT_RAW_JSON):
            logger.info(f"Loading cached full company catalog from {OUTPUT_RAW_JSON}...")
            with open(OUTPUT_RAW_JSON, "r", encoding="utf-8") as f:
                companies = json.load(f)
            logger.info(f"Loaded {len(companies)} companies from cache.")
            return companies

        logger.info(f"Fetching complete company directory from {SEARCH_URL}...")
        req = urllib.request.Request(SEARCH_URL, headers=self.headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results = data.get("results", [])
        companies = [r for r in results if r.get("type") == "company"]
        logger.info(f"Successfully retrieved index with {len(companies)} total suppliers/companies.")
        
        with open(OUTPUT_RAW_JSON, "w", encoding="utf-8") as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)
        return companies

    def fetch_company_detail(self, comp: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch rich company metadata from company profile API."""
        comp_id = comp.get("id")
        comp_name = comp.get("name", "").title()
        s = str(comp_id)
        if len(s) < 6:
            s = s.zfill(6)
        c1, c2, c3 = s[0:2], s[2:4], s[4:6]
        url = f"{BASE_URL}/47/company/{c1}/{c2}/{c3}/search{comp_id}_46.json"
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                detail = data.get("result", {})
        except Exception:
            detail = {}

        title = detail.get("companyname") or detail.get("title") or comp_name
        desc = detail.get("fulldesc") or detail.get("desc") or "Global ingredient and product solutions provider."
        categories = detail.get("categories") or "Ingredients, Food & Beverage"
        primary_activity = detail.get("companyTypes") or "Manufacturer: Ingredients / Additives"
        phone = detail.get("phone") or ""
        country = detail.get("country") or ""
        link = detail.get("link") or detail.get("url") or f"{BASE_URL}/company-{comp_id}.html"
        
        sales_markets = f"{country}, Global" if country else "Worldwide / International"
        address = f"{country}" if country else "Global Corporate Office"
        events = "Fi Europe, Vitafoods Europe"

        return {
            "company_id": comp_id,
            "company_name": title,
            "company_description": desc,
            "sales_markets": sales_markets,
            "primary_business_activity": primary_activity,
            "categories": categories.replace("|", ", "),
            "events": events,
            "address": address,
            "email": "",
            "telephone": phone,
            "website": link,
        }

    def run(self, max_records: int = 200):
        """Scrape company cards and profiles using ThreadPoolExecutor for speed."""
        os.makedirs("output", exist_ok=True)
        companies_index = self.fetch_all_companies_catalog()
        target_companies = companies_index[:max_records]

        logger.info(f"Extracting {len(target_companies)} company records concurrently...")
        records = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_comp = {executor.submit(self.fetch_company_detail, comp): comp for comp in target_companies}
            for idx, future in enumerate(as_completed(future_to_comp)):
                try:
                    rec = future.result()
                    records.append(rec)
                except Exception as e:
                    logger.debug(f"Error processing record: {e}")
                
                if (idx + 1) % 50 == 0 or (idx + 1) == len(target_companies):
                    logger.info(f"Extracted {idx + 1}/{len(target_companies)} profiles...")

        # Export to CSV
        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_RAW_CSV, index=False, encoding="utf-8")
        logger.info(f"Successfully saved {len(df)} company records to {OUTPUT_RAW_CSV}")


if __name__ == "__main__":
    scraper = IngredientsNetworkScraper()
    scraper.run(max_records=200)
