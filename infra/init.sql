-- Holiday Planner Database Init
-- Tables are auto-created by SQLAlchemy on startup
-- This file handles DB-level setup

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search on destinations

-- Create indexes (SQLAlchemy will create the tables, these run after)
-- Additional setup can go here
