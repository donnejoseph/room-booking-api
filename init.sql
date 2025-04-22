-- Create database if it doesn't exist
CREATE DATABASE booking_db;

-- Create extension for UUID if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extension for full text search if needed
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE booking_db TO booking_user; 