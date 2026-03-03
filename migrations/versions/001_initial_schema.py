"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create trends table
    op.create_table(
        'trends',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_popular', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('price_tokens', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trends_id'), 'trends', ['id'], unique=False)
    op.create_index(op.f('ix_trends_title'), 'trends', ['title'], unique=False)

    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_id'), 'assets', ['id'], unique=False)

    # Create generations table
    op.create_table(
        'generations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trend_id', sa.Integer(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('materials', sa.Text(), nullable=True),
        sa.Column('asset_ids', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('result_text', sa.Text(), nullable=True),
        sa.Column('result_assets', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('price_spent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['trend_id'], ['trends.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generations_id'), 'generations', ['id'], unique=False)

    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Integer(), nullable=False, server_default='1000'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_generations_id'), table_name='generations')
    op.drop_table('generations')
    op.drop_index(op.f('ix_assets_id'), table_name='assets')
    op.drop_table('assets')
    op.drop_index(op.f('ix_trends_title'), table_name='trends')
    op.drop_index(op.f('ix_trends_id'), table_name='trends')
    op.drop_table('trends')
