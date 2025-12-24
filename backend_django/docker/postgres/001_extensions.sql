-- PostgreSQL Extensions for ATG Education Platform
-- This file is automatically executed when PostgreSQL container starts

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for fuzzy text search (if needed)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enable unaccent for accent-insensitive search (if needed)
CREATE EXTENSION IF NOT EXISTS "unaccent";

