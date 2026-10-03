-- ==============================================================================
-- Supabase / PostgreSQL Schema for Ingredients Network Extracted Data
-- Relu Consultancy Challenge - Bonus Objective
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: ingredients_companies
DROP TABLE IF EXISTS ingredients_companies CASCADE;

CREATE TABLE ingredients_companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id INTEGER UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    company_description TEXT,
    sales_markets TEXT,
    primary_business_activity VARCHAR(255) NOT NULL,
    categories TEXT,
    events TEXT,
    address TEXT,
    email VARCHAR(255),
    telephone VARCHAR(100),
    website TEXT,
    has_herbs_spices BOOLEAN DEFAULT FALSE,
    has_physical_formats BOOLEAN DEFAULT FALSE,
    has_cognitive_health BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Indexes
CREATE INDEX idx_ingredients_name ON ingredients_companies (company_name);
CREATE INDEX idx_ingredients_activity ON ingredients_companies (primary_business_activity);
CREATE INDEX idx_ingredients_herbs ON ingredients_companies (has_herbs_spices);
CREATE INDEX idx_ingredients_physical ON ingredients_companies (has_physical_formats);
CREATE INDEX idx_ingredients_cognitive ON ingredients_companies (has_cognitive_health);

-- Full-Text Search Index on Description & Categories
CREATE INDEX idx_ingredients_search ON ingredients_companies 
USING GIN (to_tsvector('english', company_name || ' ' || COALESCE(company_description, '') || ' ' || COALESCE(categories, '')));

-- Analytical View for Category Distribution
CREATE OR REPLACE VIEW view_ingredients_summary AS
SELECT 
    COUNT(*) AS total_companies,
    COUNT(CASE WHEN has_herbs_spices THEN 1 END) AS companies_with_herbs_spices,
    COUNT(CASE WHEN has_physical_formats THEN 1 END) AS companies_with_physical_formats,
    COUNT(CASE WHEN has_cognitive_health THEN 1 END) AS companies_with_cognitive_health,
    COUNT(CASE WHEN email IS NOT NULL AND email != '' THEN 1 END) AS companies_with_email,
    COUNT(CASE WHEN telephone IS NOT NULL AND telephone != '' THEN 1 END) AS companies_with_phone
FROM ingredients_companies;
