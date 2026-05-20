"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-01 08:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_address', sa.String(length=66), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wallet_address')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index('users_wallet_address_trgm_idx', 'users', ['wallet_address'], postgresql_ops={'wallet_address': 'gin_trgm_ops'}, postgresql_using='gin')

    # Trigger function
    op.execute('''
        CREATE OR REPLACE FUNCTION set_updated_at_0001()
        RETURNS TRIGGER AS $$
        BEGIN
           NEW.updated_at = now();
           RETURN NEW;
        END;
        $$ language 'plpgsql';
    ''')
    op.execute('CREATE TRIGGER users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at_0001();')

    # Agents table
    op.create_table('agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config_json', sa.JSON(), nullable=True),
        sa.Column('price', sa.DECIMAL(precision=12, scale=6), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('price >= 0')
    )
    op.create_index(op.f('ix_agents_created_at'), 'agents', ['created_at'], unique=False)
    op.create_index(op.f('ix_agents_owner_id'), 'agents', ['owner_id'], unique=False)
    op.create_index(op.f('ix_agents_price'), 'agents', ['price'], unique=False)
    op.create_index('agents_name_trgm_idx', 'agents', ['name'], postgresql_ops={'name': 'gin_trgm_ops'}, postgresql_using='gin')
    op.execute('CREATE TRIGGER agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION set_updated_at_0001();')

    # Seed data
    op.execute("""
        INSERT INTO users (wallet_address) VALUES 
            ('0x742d35Cc6634C0532925a3b8D7c74B1f7bB9a3E1'),
            ('0x1234567890abcdef1234567890abcdef12345678');
    """)
    op.execute("""
        INSERT INTO agents (name, description, config_json, price, owner_id) VALUES 
            ('CyberAgent-1.0', 'Advanced AI agent for cybersecurity analysis', 
             '{"model": "grok-4", "tools": ["nmap", "nuclei"], "memory": 128}', 0.05, 1),
            ('MarketAnalyzer', 'Real-time market data processing agent', 
             '{"sources": ["binance", "coinbase"], "indicators": ["rsi", "macd"]}', 0.02, 2);
    """)


def downgrade() -> None:
    # Drop seed data
    op.execute("DELETE FROM agents WHERE owner_id IN (SELECT id FROM users WHERE wallet_address IN ('0x742d35Cc6634C0532925a3b8D7c74B1f7bB9a3E1', '0x1234567890abcdef1234567890abcdef12345678')); DELETE FROM users WHERE wallet_address IN ('0x742d35Cc6634C0532925a3b8D7c74B1f7bB9a3E1', '0x1234567890abcdef1234567890abcdef12345678');")

    # Drop agents table
    op.execute('DROP TRIGGER IF EXISTS agents_updated_at ON agents;')
    op.drop_index('agents_name_trgm_idx', table_name='agents', postgresql_using='gin')
    op.drop_index(op.f('ix_agents_price'), table_name='agents')
    op.drop_index(op.f('ix_agents_owner_id'), table_name='agents')
    op.drop_index(op.f('ix_agents_created_at'), table_name='agents')
    op.drop_table('agents')

    # Drop users table
    op.execute('DROP TRIGGER IF EXISTS users_updated_at ON users;')
    op.drop_index('users_wallet_address_trgm_idx', table_name='users', postgresql_using='gin')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')

    op.execute('DROP FUNCTION IF EXISTS set_updated_at_0001() CASCADE;')
