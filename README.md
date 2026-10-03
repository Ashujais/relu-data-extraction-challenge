# Relu Consultancy — Data Extraction Engineer (FTE) Hiring Challenge

Comprehensive, production-ready solution for the Relu Consultancy Data Extraction Challenge, covering live web automation, scraping, cleaning, analytical queries, and bonus database/full-stack implementations.

---

## Project Structure

```
relu-data-extraction-challenge/
│
├── disney_cruise/
│   ├── disney_cruise_scraper.py      # Automated scraper for Disney Cruise Line
│   ├── disney_cruise_cleaner.py      # Data cleaning, normalization & deduplication
│   ├── disney_cruise_analysis.py     # Solves all 5 analytical business questions
│   └── README.md                     # Module documentation & field schema
│
├── ingredients_network/
│   ├── ingredients_network_scraper.py # Automated scraper for Ingredients Network
│   ├── ingredients_network_cleaner.py # Cleans supplier directory and contact cards
│   ├── ingredients_network_analysis.py# Solves all 5 analytical market questions
│   └── README.md                     # Module documentation & bitmask details
│
├── bonus/
│   ├── app/                          # FastAPI web application & interactive UI
│   │   ├── main.py                   # FastAPI REST backend & search routes
│   │   └── templates/index.html      # Responsive Tailwind dashboard with search & pagination
│   ├── database/                     # PostgreSQL / Supabase Relational Schemas
│   │   ├── disney_schema.sql         # SQL schema, indexes, and analytical view
│   │   └── ingredients_schema.sql    # SQL schema, GIN search index, and views
│   ├── render.yaml                   # 1-click cloud deployment blueprint
│   └── README.md                     # Bonus architecture & deployment documentation
│
├── output/
│   ├── disney_cruises.csv            # Cleaned final Disney Cruise dataset
│   ├── disney_cruises_raw.csv        # Raw scraped Disney Cruise dataset
│   ├── disney_cruises_raw.json       # Raw Disney Voyage Availability Service JSON
│   ├── ingredients_network.csv       # Cleaned final Ingredients Network dataset
│   ├── ingredients_network_raw.csv   # Raw scraped Ingredients Network dataset
│   ├── ingredients_network_raw.json  # Raw search index JSON
│   └── analysis_results.json         # Compiled machine-readable answers to all 10 questions
│
├── logs/                             # Execution and pipeline log files
├── requirements.txt                  # Python dependencies
├── .env.example                      # Configuration template
├── README.md                         # Main repository guide
├── run_all.py                        # Master pipeline execution script
└── FINAL_REPORT.md                   # Comprehensive challenge evaluation report
```

---

## Quickstart & Replication

### 1. Fresh Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/relu-data-extraction-challenge.git
cd relu-data-extraction-challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Entire Pipeline in One Command
```bash
python run_all.py
```
This executes both scrapers, runs all cleaning stages, performs validation assertions, generates the final CSVs, computes all 10 answers, and outputs `output/analysis_results.json`.

### 3. Launch the Interactive Web Dashboard (Bonus)
```bash
uvicorn bonus.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to `http://localhost:8000` to interactively search, filter, and paginate through both datasets.

---

## Executive Summary of Results

### Objective 1: Disney Cruise Line
*Target Website: [disneycruise.disney.go.com/en-in/](https://disneycruise.disney.go.com/en-in/)*

| Question | Answer | Analytical Methodology |
| :--- | :---: | :--- |
| **Q1. Pacific Destination Cruises** | **2** | Filters for destinations matching `CALIFORNIA COAST` / `Pacific Coast` departing from San Diego. |
| **Q2. Total Cruises** | **125** | Total unique cleaned cruise itinerary products (covering 946 total scheduled sailings across 34 catalog pages). |
| **Q3. Holiday Cruises** | **55** | Cruises matching holiday themes ("Halloween on the High Seas", "Very Merrytime", Thanksgiving, New Year). |
| **Q4. Cruises with > 2 Booking Dates** | **53** | Itineraries where `number_of_booking_dates > 2` (up to 64 sailings on major itineraries). |
| **Q5. Departures from Miami & London** | **8** | 8 depart from London gateway (Southampton port); 0 from Miami due to Disney shifting South Florida sailings to Fort Lauderdale (Port Everglades). |

### Objective 2: Ingredients Network
*Target Website: [www.ingredientsnetwork.com](https://www.ingredientsnetwork.com/)*

| Question | Answer | Analytical Methodology |
| :--- | :---: | :--- |
| **Q1. Total Ingredients** | **41,000+** | Official platform directory index; 4,001 active in primary search index. |
| **Q2. Total Finished Products** | **21,000+** | Official platform directory index; 4,001 active in primary search index. |
| **Q3. Companies with Herbs and Spices** | **399** | Full catalog taxonomy bitmask `val=416` (Herbs & Spices). |
| **Q4. Companies with Physical Delivery Formats** | **764** | Full catalog taxonomy bitmask `val=651` (Tablets, Capsules, Softgels, Powders). |
| **Q5. Companies in Cognitive & Mental Health** | **587** | Full catalog taxonomy bitmask `val=673` (Cognitive & Mental Health formulations). |

---

## Google Colab Execution Instructions
To run this project inside Google Colab:
```python
# 1. Clone repository
!git clone https://github.com/your-username/relu-data-extraction-challenge.git
%cd relu-data-extraction-challenge

# 2. Install dependencies
!pip install -r requirements.txt

# 3. Execute master pipeline
!python run_all.py

# 4. View results
import json
with open('output/analysis_results.json') as f:
    print(json.dumps(json.load(f), indent=2))
```
