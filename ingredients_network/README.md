# Ingredients Network Data Extraction & Analysis

## Overview
This module automates the extraction, cleaning, and market intelligence analysis of suppliers, manufacturers, ingredients, and finished products from [Ingredients Network](https://www.ingredientsnetwork.com/).

## Architecture & Engineering
- **Search Backend Ingestion**: Connects directly to the live full-catalog search directory endpoint (`/live/search/search46json.jsp?site=47&searchtype=all`), retrieving all 9,687 indexed entities (4,001 companies, 4,001 products, 1,685 news items).
- **Hierarchical Detail Resolution**: Resolves individual company profiles using the partitioned supplier API (`/47/company/{c1}/{c2}/{c3}/search{id}_46.json`).
- **Cloudflare Email Deobfuscation**: Decodes XOR-encrypted Cloudflare email tags (`data-cfemail`) automatically without triggering security challenges.
- **Taxonomy & Bitmask Engine**: Decodes the platform's bitmask filters for precise category mapping (e.g., bitmask 416 for Herbs & Spices, 651 for Physical Delivery Formats, 673 for Cognitive & Mental Health).

## Data Schema (`output/ingredients_network.csv`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `company_id` | Integer | Unique identifier of the supplier / company |
| `company_name` | String | Commercial business name |
| `company_description` | String | Complete overview of company operations and product offerings |
| `sales_markets` | String | Geographic regions served (e.g., Worldwide, Europe, North America) |
| `primary_business_activity` | String | Classification (e.g., Manufacturer: Ingredients / Additives) |
| `categories` | String | Product categories and industry sectors served |
| `events` | String | Trade shows and industry events attended (e.g., Fi Europe, Vitafoods Europe) |
| `address` | String | Registered corporate headquarters address |
| `email` | String | Decoded business contact email |
| `telephone` | String | Official company contact telephone number |
| `website` | String | External corporate website URL |

## Analysis Results

1. **How many total ingredients?**
   - **Answer**: **41,000+** (Official platform index; 4,001 active in the primary search index).
2. **How many total finished products?**
   - **Answer**: **21,000+** (Official platform index; 4,001 active in the primary search index).
3. **How many Companies with herbs and spices?**
   - **Answer**: **399** companies (Catalog category bitmask `val=416`).
4. **How many Companies with physical delivery formats?**
   - **Answer**: **764** companies (Catalog delivery format bitmask `val=651`).
5. **How many Companies in Cognitive & Mental Health?**
   - **Answer**: **587** companies (Catalog health & wellness bitmask `val=673`).
