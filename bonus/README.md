# Bonus Deliverables: Database Architecture & Interactive Application

## 1. Overview
As part of the Relu Consultancy Data Extraction Challenge, this bonus module provides:
1. **Production-Ready Relational Database Schemas** for Supabase / PostgreSQL (`bonus/database/`).
2. **Interactive FastAPI Web Dashboard** with real-time search, category filtering, pagination, and KPI metrics cards (`bonus/app/`).
3. **Deployment Configuration** (`bonus/render.yaml`) ready for 1-click cloud deployment on Render.com or Railway.

---

## 2. Database Schemas (`bonus/database/`)

### A. Disney Cruise Schema (`disney_schema.sql`)
- **Table**: `disney_cruises`
- **Fields**: UUID primary key, `product_id`, `sailing_id`, `cruise_title`, `ship`, `destination`, `destination_clean`, `geo_area`, `departure_port`, `duration_nights`, `number_of_booking_dates`, `package_code`, `currency`, `starting_price`, `stateroom_classes`, `image_url`, `booking_url`, timestamps.
- **Indexes**: Composite b-tree indexes on `destination`, `departure_port`, `ship`, and `number_of_booking_dates` for sub-millisecond query execution.
- **Analytical View**: `view_disney_destination_summary` aggregates average cruise duration, pricing, and sailing availability by destination.

### B. Ingredients Network Schema (`ingredients_schema.sql`)
- **Table**: `ingredients_companies`
- **Fields**: UUID primary key, `company_id`, `company_name`, `company_description`, `sales_markets`, `primary_business_activity`, `categories`, `events`, `address`, `email`, `telephone`, `website`, boolean flags (`has_herbs_spices`, `has_physical_formats`, `has_cognitive_health`), timestamps.
- **Search Capabilities**: PostgreSQL Full-Text Search index (GIN) on combined company name, overview, and sector categories.
- **Analytical View**: `view_ingredients_summary` computes directory category breakdowns and contact completeness metrics.

---

## 3. Web Dashboard (`bonus/app/`)

### Features
- **FastAPI Engine**: High-performance asynchronous REST backend.
- **Tailwind CSS UI**: Modern responsive design with dark mode styling, intuitive tab switching, and metric cards.
- **Search & Filter Controls**: Real-time debounced search by name, vessel, port, or activity, with dropdown destination filters.
- **Resilient Fallback**: Automatically serves data from the local generated CSVs (`output/disney_cruises.csv` and `output/ingredients_network.csv`) even when remote database credentials are not set.

### Running the App Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn bonus.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at `http://localhost:8000`.

---

## 4. Cloud Deployment (`render.yaml`)
Deploy instantly to Render:
1. Connect your GitHub repository to Render.
2. Render detects `bonus/render.yaml` and provisions the Python web service.
3. Configure `SUPABASE_URL` and `SUPABASE_KEY` environment variables if connecting to a live Supabase instance.
