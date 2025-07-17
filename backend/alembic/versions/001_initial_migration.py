"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('income', sa.Integer(), nullable=True),
        sa.Column('risk_tolerance', sa.String(), nullable=True),
        sa.Column('financial_goals', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('merchant', sa.String(), nullable=True),
        sa.Column('account_type', sa.String(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_date_amount', 'transactions', ['date', 'amount'], unique=False)
    op.create_index('idx_user_category', 'transactions', ['user_id', 'category'], unique=False)
    op.create_index('idx_user_date', 'transactions', ['user_id', 'date'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)

    # Create financial_goals table
    op.create_table('financial_goals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_amount', sa.Float(), nullable=False),
        sa.Column('current_amount', sa.Float(), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_goals_id'), 'financial_goals', ['id'], unique=False)

    # Create chat_history table
    op.create_table('chat_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=True),
        sa.Column('context_data', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_history_id'), 'chat_history', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_history_id'), table_name='chat_history')
    op.drop_table('chat_history')
    op.drop_index(op.f('ix_financial_goals_id'), table_name='financial_goals')
    op.drop_table('financial_goals')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_index('idx_user_date', table_name='transactions')
    op.drop_index('idx_user_category', table_name='transactions')
    op.drop_index('idx_date_amount', table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')