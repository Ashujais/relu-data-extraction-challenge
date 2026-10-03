-- ==============================================================================
-- Supabase / PostgreSQL Schema for Disney Cruise Line Extracted Data
-- Relu Consultancy Challenge - Bonus Objective
-- ==============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: disney_cruises
DROP TABLE IF EXISTS disney_cruises CASCADE;

CREATE TABLE disney_cruises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(100) NOT NULL,
    sailing_id VARCHAR(100),
    cruise_title VARCHAR(255) NOT NULL,
    ship VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    destination_clean VARCHAR(100),
    geo_area VARCHAR(100),
    departure_port VARCHAR(100) NOT NULL,
    duration_nights INTEGER NOT NULL DEFAULT 0,
    number_of_booking_dates INTEGER NOT NULL DEFAULT 0,
    package_code VARCHAR(100),
    currency VARCHAR(10) DEFAULT 'USD',
    starting_price NUMERIC(10, 2),
    stateroom_classes TEXT,
    image_url TEXT,
    booking_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Indexes
CREATE INDEX idx_disney_destination ON disney_cruises (destination);
CREATE INDEX idx_disney_clean_destination ON disney_cruises (destination_clean);
CREATE INDEX idx_disney_departure_port ON disney_cruises (departure_port);
CREATE INDEX idx_disney_ship ON disney_cruises (ship);
CREATE INDEX idx_disney_booking_dates ON disney_cruises (number_of_booking_dates);

-- Analytical View for Dashboard
CREATE OR REPLACE VIEW view_disney_destination_summary AS
SELECT 
    destination_clean AS destination,
    COUNT(*) AS total_cruises,
    ROUND(AVG(duration_nights), 1) AS avg_duration_nights,
    ROUND(AVG(starting_price), 2) AS avg_starting_price,
    SUM(number_of_booking_dates) AS total_available_sailings
FROM disney_cruises
GROUP BY destination_clean
ORDER BY total_cruises DESC;
