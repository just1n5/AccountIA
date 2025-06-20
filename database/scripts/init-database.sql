-- ================================
-- AccountIA - Database Initialization
-- PostgreSQL Compatible Version
-- ================================

-- Note: In Docker environment, the main database is already created
-- by environment variables, so we don't need to create it here

-- Create user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'accountia_user') THEN
        CREATE USER accountia_user WITH PASSWORD 'accountia_password';
    END IF;
END
$$;

-- Grant privileges on current database
GRANT ALL PRIVILEGES ON DATABASE accountia_dev TO accountia_user;

-- Enable required extensions
-- UUID extension for UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pgcrypto for encryption
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- vector extension for AI/ML (if available)
-- Note: This extension might not be available in all PostgreSQL installations
-- CREATE EXTENSION IF NOT EXISTS "vector";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
-- public schema already exists by default
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant schema privileges
GRANT ALL ON SCHEMA auth TO accountia_user;
GRANT ALL ON SCHEMA public TO accountia_user;
GRANT ALL ON SCHEMA audit TO accountia_user;

-- Grant usage and create privileges on schemas
GRANT USAGE, CREATE ON SCHEMA auth TO accountia_user;
GRANT USAGE, CREATE ON SCHEMA public TO accountia_user;
GRANT USAGE, CREATE ON SCHEMA audit TO accountia_user;

-- Grant privileges on all current and future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT ALL ON TABLES TO accountia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO accountia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT ALL ON TABLES TO accountia_user;

-- Grant privileges on all current and future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT ALL ON SEQUENCES TO accountia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO accountia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT ALL ON SEQUENCES TO accountia_user;

-- Comments
COMMENT ON SCHEMA auth IS 'Authentication and user management';
COMMENT ON SCHEMA audit IS 'Audit logs and tracking';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'AccountIA database initialization completed successfully';
END
$$;