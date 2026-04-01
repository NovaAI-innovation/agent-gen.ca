-- agent-gen.ca PostgreSQL 16 Schema (3NF normalized)
-- Extensions for advanced features
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (wallet_address UNIQUE constraint)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(66) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX users_wallet_address_idx ON users (wallet_address);
CREATE INDEX users_wallet_address_trgm_idx ON users USING gin (wallet_address gin_trgm_ops);
CREATE INDEX users_created_at_idx ON users (created_at);
CREATE TRIGGER users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION now();

-- Agents table (owner_id FK to users)
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config_json JSONB,
    price DECIMAL(12,6) CHECK (price >= 0),
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX agents_owner_id_idx ON agents (owner_id);
CREATE INDEX agents_price_idx ON agents (price);
CREATE INDEX agents_created_at_idx ON agents (created_at);
CREATE INDEX agents_name_trgm_idx ON agents USING gin (name gin_trgm_ops);
CREATE TRIGGER agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION now();

-- Seed data (sample user + agent)
INSERT INTO users (wallet_address) VALUES 
    ('0x742d35Cc6634C0532925a3b8D7c74B1f7bB9a3E1'),
    ('0x1234567890abcdef1234567890abcdef12345678');

INSERT INTO agents (name, description, config_json, price, owner_id) VALUES 
    ('CyberAgent-1.0', 'Advanced AI agent for cybersecurity analysis', 
     '{"model": "grok-4", "tools": ["nmap", "nuclei"], "memory": 128}', 0.05, 1),
    ('MarketAnalyzer', 'Real-time market data processing agent', 
     '{"sources": ["binance", "coinbase"], "indicators": ["rsi", "macd"]}', 0.02, 2);

-- Verification queries
-- SELECT * FROM users;
-- SELECT * FROM agents WHERE owner_id = 1;
-- SELECT u.wallet_address, COUNT(a.id) as agent_count FROM users u LEFT JOIN agents a ON u.id = a.owner_id GROUP BY u.id;