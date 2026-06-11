-- Create schemas for better organization
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant usage on schemas to application user
GRANT USAGE ON SCHEMA auth TO auth_db_user;
GRANT USAGE ON SCHEMA audit TO auth_db_user;

-- Set default search path for the application user
ALTER ROLE auth_db_user SET search_path TO auth;