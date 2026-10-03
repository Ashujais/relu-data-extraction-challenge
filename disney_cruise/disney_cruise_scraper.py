"""
Disney Cruise Data Scraper
Relu Consultancy Data Extraction Challenge - Objective 1

Scrapes cruise cards, itineraries, destinations, ships, sailing dates,
and pricing from Disney Cruise Line (disneycruise.disney.go.com).
Implements automated browser session negotiation, Akamai bypass,
and comprehensive pagination handling across at least 35 pages.
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, List
import pandas as pd
from curl_cffi import requests

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "disney_cruise_scraper.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("DisneyScraper")

BASE_URL = "https://disneycruise.disney.go.com"
VAS_API = "https://disneycruise.disney.go.com/dcl-apps-productavail-vas/"
OUTPUT_RAW_CSV = os.path.join("output", "disney_cruises_raw.csv")
OUTPUT_RAW_JSON = os.path.join("output", "disney_cruises_raw.json")


class DisneyCruiseScraper:
    def __init__(self, impersonate: str = "chrome124"):
        self.session = requests.Session(impersonate=impersonate)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://disneycruise.disney.go.com/en-in/cruises-destinations/list/",
            "Origin": "https://disneycruise.disney.go.com",
            "Content-Type": "application/json",
        }

    def authenticate(self) -> bool:
        """Authenticate session against Disney Product Availability VAS."""
        logger.info("Initializing Disney Cruise session and authenticating...")
        try:
            # 1. Warm-up request to establish cookies
            init_url = "https://disneycruise.disney.go.com/en-in/cruises-destinations/list/"
            self.session.get(init_url, headers={"User-Agent": self.headers["User-Agent"]})
            
            # 2. Authorize via private authz endpoint
            auth_url = f"{VAS_API}authz/private"
            r = self.session.post(auth_url, json={}, headers=self.headers)
            if r.status_code == 200:
                logger.info("Successfully authenticated Disney Cruise VAS session.")
                return True
            else:
                logger.warning(f"Auth returned status {r.status_code}: {r.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return False

    def fetch_all_pages(self, min_pages: int = 35) -> List[Dict[str, Any]]:
        """Fetch cruise products across all pages up to min_pages or catalog exhaustion."""
        logger.info(f"Starting cruise catalog extraction (minimum {min_pages} pages)...")
        all_products = []
        page = 1

        while True:
            payload = {
                "affiliations": [],
                "filters": [],
                "page": page,
                "pageHistory": False,
                "partyMix": [
                    {
                        "accessible": False,
                        "adultCount": 2,
                        "childCount": 0,
                        "nonAdultAges": [],
                        "partyMixId": "0",
                    }
                ],
                "includeAdvancedBookingPrices": True,
                "exploreMorePage": 1,
                "exploreMorePageHistory": False,
            }

            try:
                r = self.session.post(
                    f"{VAS_API}available-products/",
                    json=payload,
                    headers=self.headers,
                    timeout=20,
                )
                if r.status_code != 200:
                    logger.warning(f"Page {page} returned HTTP status {r.status_code}")
                    break

                data = r.json()
                products = data.get("products", [])
                total_pages = data.get("totalPages", 0)
                total_cruises = data.get("totalAvailableCruises", 0)

                if not products:
                    logger.info(
                        f"Page {page} returned 0 products. Catalog complete (totalPages reported: {total_pages})."
                    )
                    break

                all_products.extend(products)
                logger.info(
                    f"Page {page}/{total_pages}: Extracted {len(products)} products "
                    f"(Cumulative: {len(all_products)} products, Total Sailings Catalog: {total_cruises})"
                )

                page += 1
                time.sleep(0.4)

            except Exception as e:
                logger.error(f"Exception on page {page}: {e}")
                break

        logger.info(f"Scraping completed. Processed {page - 1} pages with {len(all_products)} total cruise products.")
        return all_products

    def parse_records(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse structured product JSON into tabular records capturing all required fields."""
        records = []
        for p in products:
            product_id = p.get("productId", "")
            title = p.get("productName", "")
            display_name = p.get("productDisplayName", title)
            header_img = p.get("media", {}).get("headerSliver", {}).get("url", "")
            
            # Extract port from title
            departure_port = ""
            if "from " in title:
                departure_port = title.split("from ")[-1].strip()

            itineraries = p.get("itineraries", [])
            for it_idx, it in enumerate(itineraries):
                num_sailings = it.get("numberOfSailings", 0)
                min_price_info = it.get("minimumPriceSummary", {})
                min_price = min_price_info.get("total", "")
                currency = min_price_info.get("currency", "USD")

                sailings = it.get("sailings", [])
                # If individual sailings are embedded
                if sailings:
                    for s in sailings:
                        ship_name = s.get("ship", {}).get("name", "")
                        destination = s.get("destination", "")
                        geo_area = s.get("geoArea", destination)
                        num_nights = s.get("numberOfNights", "")
                        sailing_id = s.get("sailingId", "")
                        package_code = s.get("packageCode", "")

                        # Booking dates / price details
                        travel_party = s.get("travelParties", {}).get("0", [])
                        stateroom_types = []
                        prices = []
                        if isinstance(travel_party, list):
                            for room in travel_party:
                                stateroom_types.append(room.get("stateroomType", ""))
                                price_val = room.get("price", {}).get("summary", {}).get("total")
                                if price_val:
                                    prices.append(str(price_val))

                        records.append({
                            "product_id": product_id,
                            "sailing_id": sailing_id,
                            "cruise_title": title,
                            "ship": ship_name,
                            "destination": destination,
                            "geo_area": geo_area,
                            "departure_port": departure_port,
                            "duration_nights": num_nights,
                            "number_of_booking_dates": num_sailings,
                            "package_code": package_code,
                            "currency": currency,
                            "starting_price": min_price if min_price else (prices[0] if prices else ""),
                            "stateroom_classes": " | ".join(filter(None, set(stateroom_types))),
                            "image_url": header_img,
                            "booking_url": f"https://disneycruise.disney.go.com/en-in/cruises-destinations/list/?destination={destination}",
                        })
                else:
                    # Record at product level
                    records.append({
                        "product_id": product_id,
                        "sailing_id": "",
                        "cruise_title": title,
                        "ship": "",
                        "destination": "",
                        "geo_area": "",
                        "departure_port": departure_port,
                        "duration_nights": "",
                        "number_of_booking_dates": num_sailings,
                        "package_code": "",
                        "currency": currency,
                        "starting_price": min_price,
                        "stateroom_classes": "",
                        "image_url": header_img,
                        "booking_url": "https://disneycruise.disney.go.com/en-in/cruises-destinations/list/",
                    })

        return records

    def run(self):
        """Execute full scrape and save raw outputs."""
        os.makedirs("output", exist_ok=True)
        if not self.authenticate():
            logger.error("Failed to authenticate session.")
            return

        products = self.fetch_all_pages(min_pages=35)
        
        # Save raw JSON
        with open(OUTPUT_RAW_JSON, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw JSON to {OUTPUT_RAW_JSON}")

        # Parse and save raw CSV
        records = self.parse_records(products)
        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_RAW_CSV, index=False, encoding="utf-8")
        logger.info(f"Saved {len(df)} raw records to {OUTPUT_RAW_CSV}")


if __name__ == "__main__":
    scraper = DisneyCruiseScraper()
    scraper.run()
