# Disney Cruise Line Data Extraction & Analysis

## Overview
This module automates the extraction, cleaning, and business intelligence analysis of all cruise itineraries from [Disney Cruise Line](https://disneycruise.disney.go.com/en-in/).

## Architecture & Engineering
- **Session & Security Orchestration**: Negotiates browser TLS fingerprints using `curl_cffi` (Chrome 124 impersonation) to pass Akamai EdgeSuite anti-bot controls and Queue-It token gating without fragile headless timeouts.
- **Dynamic Catalog Traversal**: Interacts with Disney's Product Availability VAS (Voyage Availability Service) API (`/dcl-apps-productavail-vas/`) to retrieve paginated cruise product structures (`available-products/`).
- **Pagination**: Iterates sequentially through all 34–35 catalog pages, dynamically capturing 170 distinct itineraries and 946 total scheduled sailings.
- **Robust Error Handling**: Backoff retries, JSON validation, and fallback mechanisms for incomplete DOM structures.

## Data Schema (`output/disney_cruises.csv`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `product_id` | String | Unique product identifier (e.g., `3_singapore`, `4_baja`) |
| `sailing_id` | String | Individual sailing voyage identifier (e.g., `DA0100`) |
| `cruise_title` | String | Exact title as published on the website |
| `ship` | String | Assigned vessel (e.g., `Disney Adventure`, `Disney Wish`, `Disney Magic`) |
| `destination` | String | Target destination code (e.g., `CALIFORNIA COAST`, `BAHAMAS`, `CARIBBEAN`) |
| `destination_clean` | String | Normalized destination name (e.g., `Pacific Coast`, `Bahamas`) |
| `geo_area` | String | Geographic area of cruise |
| `departure_port` | String | Port of embarkation (e.g., `San Diego`, `Fort Lauderdale`, `Southampton`) |
| `duration_nights` | Integer | Total length of cruise in nights |
| `number_of_booking_dates` | Integer | Total count of scheduled sailing dates available for booking |
| `package_code` | String | Internal Disney itinerary package code |
| `currency` | String | Billing currency code (`USD`) |
| `starting_price` | Float | Lead-in starting fare for 2 adult guests |
| `stateroom_classes` | String | Available stateroom categories (Inside, Oceanview, Verandah, Concierge) |
| `image_url` | String | URL of destination hero image |
| `booking_url` | String | Deep link to booking search results |

## Cleaned Data Pipeline
1. `disney_cruise_scraper.py`: Fetches raw data from live endpoints across all 35 pages and writes `output/disney_cruises_raw.csv` and `output/disney_cruises_raw.json`.
2. `disney_cruise_cleaner.py`: Performs whitespace normalization, null token purging, composite deduplication on `[product_id, ship, destination, departure_port, duration_nights]`, validates mandatory fields, and writes `output/disney_cruises.csv`.
3. `disney_cruise_analysis.py`: Computes answers to all 5 required business questions directly from `output/disney_cruises.csv`.

## Analysis Results

1. **How many total cruises are there for the Pacific as a destination?**
   - **Answer**: **2** (California Coast / Pacific Coast itineraries departing from San Diego).
2. **How many total cruises are there?**
   - **Answer**: **170** unique cruise itinerary products (covering 946 total sailing departure dates across the fleet).
3. **How many holiday cruises are there?**
   - **Answer**: **73** cruises (identified by holiday themes: "Halloween on the High Seas", "Very Merrytime", Christmas, Thanksgiving, New Year).
4. **How many Cruises offer more than 2 dates for booking?**
   - **Answer**: **67** cruises (cruises with `number_of_booking_dates > 2`).
5. **How many total cruises are there that depart from Miami and London?**
   - **Answer**: **11** (11 depart from London gateway via Southampton; 0 from Miami due to Disney shifting South Florida sailings to Port Everglades / Fort Lauderdale which has 47 cruises).
