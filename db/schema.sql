-- agent-gen.ca PostgreSQL 16 Schema
-- Community marketplace for MCP servers, agent skills, custom AI agents, and packs
-- Auth: Solana Phantom wallet (ed25519 public key, base58, 44 chars)

CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE listing_type AS ENUM ('mcp_server', 'agent_skill', 'custom_agent', 'pack');
CREATE TYPE purchase_status AS ENUM ('pending', 'confirmed', 'failed');

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_address VARCHAR(44) NOT NULL,          -- Solana base58 public key
    username      VARCHAR(50),
    bio           TEXT,
    avatar_url    TEXT,
    reputation_score INT NOT NULL DEFAULT 0,
    is_verified   BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX users_wallet_address_idx ON users (wallet_address);
CREATE UNIQUE INDEX users_username_idx ON users (LOWER(username)) WHERE username IS NOT NULL;
CREATE INDEX users_wallet_trgm_idx ON users USING gin (wallet_address gin_trgm_ops);
CREATE INDEX users_reputation_idx ON users (reputation_score DESC);

-- ============================================================
-- AUTH NONCES (challenge/response for Phantom wallet sign-in)
-- ============================================================

CREATE TABLE auth_nonces (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_address VARCHAR(44) NOT NULL,
    nonce         VARCHAR(64) NOT NULL,
    expires_at    TIMESTAMPTZ NOT NULL,
    used          BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX auth_nonces_nonce_idx ON auth_nonces (nonce);
CREATE INDEX auth_nonces_wallet_idx ON auth_nonces (wallet_address);
CREATE INDEX auth_nonces_expires_idx ON auth_nonces (expires_at);

-- ============================================================
-- CATEGORIES (self-referential for nesting)
-- ============================================================

CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) NOT NULL,
    description TEXT,
    icon        VARCHAR(50),
    parent_id   INT REFERENCES categories(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX categories_slug_idx ON categories (slug);

-- ============================================================
-- TAGS
-- ============================================================

CREATE TABLE tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE UNIQUE INDEX tags_name_idx ON tags (LOWER(name));

-- ============================================================
-- LISTINGS
-- ============================================================

CREATE TABLE listings (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type             listing_type NOT NULL,
    title            VARCHAR(255) NOT NULL,
    slug             VARCHAR(255) NOT NULL,
    description      TEXT,
    long_description TEXT,
    owner_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_published     BOOLEAN NOT NULL DEFAULT false,
    is_featured      BOOLEAN NOT NULL DEFAULT false,
    price_sol        DECIMAL(18,9) NOT NULL DEFAULT 0 CHECK (price_sol >= 0),
    download_count   INT NOT NULL DEFAULT 0,
    view_count       INT NOT NULL DEFAULT 0,
    avg_rating       DECIMAL(3,2) CHECK (avg_rating >= 1 AND avg_rating <= 5),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX listings_slug_idx ON listings (slug);
CREATE INDEX listings_type_idx ON listings (type);
CREATE INDEX listings_owner_idx ON listings (owner_id);
CREATE INDEX listings_published_idx ON listings (is_published) WHERE is_published = true;
CREATE INDEX listings_featured_idx ON listings (is_featured) WHERE is_featured = true;
CREATE INDEX listings_price_idx ON listings (price_sol);
CREATE INDEX listings_downloads_idx ON listings (download_count DESC);
CREATE INDEX listings_created_idx ON listings (created_at DESC);
CREATE INDEX listings_title_trgm_idx ON listings USING gin (title gin_trgm_ops);
CREATE INDEX listings_desc_trgm_idx ON listings USING gin (description gin_trgm_ops);

-- ============================================================
-- LISTING VERSIONS (semver history with config/manifest)
-- ============================================================

CREATE TABLE listing_versions (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id            UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    version               VARCHAR(20) NOT NULL,         -- semver e.g. "1.2.3"
    changelog             TEXT,
    config_json           JSONB,                        -- full manifest/config/schema
    install_instructions  TEXT,
    is_latest             BOOLEAN NOT NULL DEFAULT true,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX listing_versions_unique_idx ON listing_versions (listing_id, version);
CREATE INDEX listing_versions_listing_idx ON listing_versions (listing_id);
CREATE INDEX listing_versions_latest_idx ON listing_versions (listing_id, is_latest) WHERE is_latest = true;

-- ============================================================
-- LISTING TAXONOMY (join tables)
-- ============================================================

CREATE TABLE listing_categories (
    listing_id  UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (listing_id, category_id)
);

CREATE TABLE listing_tags (
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    tag_id     INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (listing_id, tag_id)
);

CREATE INDEX listing_tags_tag_idx ON listing_tags (tag_id);

-- ============================================================
-- PACK ITEMS (bundle: pack listing → contained listings)
-- ============================================================

CREATE TABLE pack_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pack_listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    item_listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    position        INT NOT NULL DEFAULT 0,
    note            TEXT,
    CONSTRAINT pack_items_no_self CHECK (pack_listing_id <> item_listing_id),
    UNIQUE (pack_listing_id, item_listing_id)
);

CREATE INDEX pack_items_pack_idx ON pack_items (pack_listing_id);

-- ============================================================
-- REVIEWS & RATINGS
-- ============================================================

CREATE TABLE reviews (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id           UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    reviewer_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating               SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title                VARCHAR(255),
    body                 TEXT,
    is_verified_purchase BOOLEAN NOT NULL DEFAULT false,
    helpful_count        INT NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (listing_id, reviewer_id)  -- one review per user per listing
);

CREATE INDEX reviews_listing_idx ON reviews (listing_id);
CREATE INDEX reviews_reviewer_idx ON reviews (reviewer_id);
CREATE INDEX reviews_rating_idx ON reviews (listing_id, rating);

CREATE TABLE review_helpful (
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    user_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (review_id, user_id)
);

-- ============================================================
-- SOCIAL: FOLLOWS
-- ============================================================

CREATE TABLE user_follows (
    follower_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    CONSTRAINT user_follows_no_self CHECK (follower_id <> following_id)
);

CREATE INDEX user_follows_following_idx ON user_follows (following_id);

-- ============================================================
-- TRANSACTIONS: PURCHASES
-- ============================================================

CREATE TABLE purchases (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id   UUID NOT NULL REFERENCES listings(id) ON DELETE RESTRICT,
    buyer_id     UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    seller_id    UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    price_sol    DECIMAL(18,9) NOT NULL CHECK (price_sol > 0),
    tx_signature VARCHAR(88),                           -- Solana transaction signature
    status       purchase_status NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX purchases_buyer_idx ON purchases (buyer_id);
CREATE INDEX purchases_seller_idx ON purchases (seller_id);
CREATE INDEX purchases_listing_idx ON purchases (listing_id);
CREATE UNIQUE INDEX purchases_tx_sig_idx ON purchases (tx_signature) WHERE tx_signature IS NOT NULL;

-- ============================================================
-- TRANSACTIONS: TIPS
-- ============================================================

CREATE TABLE tips (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    to_user_id   UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    listing_id   UUID REFERENCES listings(id) ON DELETE SET NULL,
    amount_sol   DECIMAL(18,9) NOT NULL CHECK (amount_sol > 0),
    tx_signature VARCHAR(88) NOT NULL,
    message      TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tips_no_self CHECK (from_user_id <> to_user_id)
);

CREATE UNIQUE INDEX tips_tx_sig_idx ON tips (tx_signature);
CREATE INDEX tips_to_user_idx ON tips (to_user_id);
CREATE INDEX tips_from_user_idx ON tips (from_user_id);

-- ============================================================
-- USER STATE: DOWNLOADS
-- ============================================================

CREATE TABLE downloads (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES listing_versions(id) ON DELETE CASCADE,
    user_id    UUID REFERENCES users(id) ON DELETE SET NULL,  -- nullable for anon
    ip_hash    VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX downloads_listing_idx ON downloads (listing_id);
CREATE INDEX downloads_user_idx ON downloads (user_id) WHERE user_id IS NOT NULL;
CREATE INDEX downloads_created_idx ON downloads (created_at DESC);

-- ============================================================
-- USER STATE: SAVES (BOOKMARKS)
-- ============================================================

CREATE TABLE user_saves (
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, listing_id)
);

CREATE INDEX user_saves_listing_idx ON user_saves (listing_id);

-- ============================================================
-- USER STATE: INSTALL HISTORY
-- ============================================================

CREATE TABLE install_history (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id   UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    version_id   UUID NOT NULL REFERENCES listing_versions(id) ON DELETE CASCADE,
    installed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX install_history_user_idx ON install_history (user_id);
CREATE INDEX install_history_listing_idx ON install_history (listing_id);

-- ============================================================
-- CURATION: COLLECTIONS
-- ============================================================

CREATE TABLE collections (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    curator_id  UUID REFERENCES users(id) ON DELETE SET NULL,
    is_official BOOLEAN NOT NULL DEFAULT false,
    position    INT NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX collections_official_idx ON collections (is_official) WHERE is_official = true;
CREATE INDEX collections_position_idx ON collections (position);

CREATE TABLE collection_items (
    collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    listing_id    UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    position      INT NOT NULL DEFAULT 0,
    PRIMARY KEY (collection_id, listing_id)
);

CREATE INDEX collection_items_listing_idx ON collection_items (listing_id);

-- ============================================================
-- TRIGGERS: updated_at auto-update
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER listings_updated_at
    BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- SEED DATA
-- ============================================================

INSERT INTO categories (name, slug, description, icon) VALUES
    ('MCP Servers',    'mcp-servers',    'Model Context Protocol server packages',     'server'),
    ('Agent Skills',   'agent-skills',   'Reusable skills and tools for AI agents',    'zap'),
    ('Custom Agents',  'custom-agents',  'Full agent configurations and personalities', 'bot'),
    ('Packs',          'packs',          'Curated bundles of marketplace items',        'package'),
    ('Productivity',   'productivity',   'Productivity and workflow automation',        'briefcase'),
    ('Development',    'development',    'Software development tools and agents',       'code'),
    ('Data & Analytics', 'data-analytics', 'Data processing and analysis',             'bar-chart'),
    ('Security',       'security',       'Security analysis and testing agents',        'shield');

INSERT INTO tags (name) VALUES
    ('typescript'), ('python'), ('rust'), ('filesystem'), ('database'),
    ('web-search'), ('code-generation'), ('rag'), ('memory'), ('vision'),
    ('free'), ('open-source'), ('official'), ('community'), ('featured');
