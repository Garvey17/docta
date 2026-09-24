"""Initial database schema with Log Everything telemetry.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-24 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create meals table
    op.create_table(
        'meals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('image_url', sa.String(length=1024), nullable=True),
        sa.Column('meal_type', sa.String(length=50), nullable=False, server_default='lunch'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('logged_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_calories_kcal', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_protein_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_fat_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_carbs_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_fiber_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_sodium_mg', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_calcium_mg', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_iron_mg', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meals_id'), 'meals', ['id'], unique=False)
    op.create_index(op.f('ix_meals_user_id'), 'meals', ['user_id'], unique=False)
    op.create_index(op.f('ix_meals_logged_at'), 'meals', ['logged_at'], unique=False)

    # 3. Create meal_items table
    op.create_table(
        'meal_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('meal_id', sa.Uuid(), nullable=False),
        sa.Column('item_id', sa.String(length=100), nullable=True),
        sa.Column('food_name', sa.String(length=255), nullable=False),
        sa.Column('predicted_dish_id', sa.String(length=100), nullable=False),
        sa.Column('final_dish_id', sa.String(length=100), nullable=False),
        sa.Column('label_modified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('bounding_box', sa.JSON(), nullable=True),
        sa.Column('selected_unit_id', sa.String(length=100), nullable=True),
        sa.Column('selected_quantity', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('gram_weight', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('calories_kcal', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('protein_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fat_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('carbs_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fiber_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('sodium_mg', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('calcium_mg', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('iron_mg', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['meal_id'], ['meals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_items_id'), 'meal_items', ['id'], unique=False)
    op.create_index(op.f('ix_meal_items_meal_id'), 'meal_items', ['meal_id'], unique=False)

    # 4. Create meal_item_feedback_logs table (Active Learning Telemetry)
    op.create_table(
        'meal_item_feedback_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('meal_id', sa.Uuid(), nullable=True),
        sa.Column('meal_item_id', sa.Uuid(), nullable=True),
        sa.Column('image_url', sa.String(length=1024), nullable=True),
        sa.Column('predicted_dish_id', sa.String(length=100), nullable=False),
        sa.Column('predicted_confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('bounding_box', sa.JSON(), nullable=True),
        sa.Column('final_dish_id', sa.String(length=100), nullable=False),
        sa.Column('label_modified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('selected_unit_id', sa.String(length=100), nullable=False),
        sa.Column('selected_quantity', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('calculated_gram_weight', sa.Float(), nullable=False),
        sa.Column('custom_weight_entered_g', sa.Float(), nullable=True),
        sa.Column('logged_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['meal_id'], ['meals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['meal_item_id'], ['meal_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_item_feedback_logs_id'), 'meal_item_feedback_logs', ['id'], unique=False)
    op.create_index(op.f('ix_meal_item_feedback_logs_user_id'), 'meal_item_feedback_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_meal_item_feedback_logs_meal_id'), 'meal_item_feedback_logs', ['meal_id'], unique=False)
    op.create_index(op.f('ix_meal_item_feedback_logs_predicted_dish_id'), 'meal_item_feedback_logs', ['predicted_dish_id'], unique=False)
    op.create_index(op.f('ix_meal_item_feedback_logs_final_dish_id'), 'meal_item_feedback_logs', ['final_dish_id'], unique=False)
    op.create_index(op.f('ix_meal_item_feedback_logs_label_modified'), 'meal_item_feedback_logs', ['label_modified'], unique=False)
    op.create_index(op.f('ix_meal_item_feedback_logs_logged_at'), 'meal_item_feedback_logs', ['logged_at'], unique=False)


def downgrade() -> None:
    op.drop_table('meal_item_feedback_logs')
    op.drop_table('meal_items')
    op.drop_table('meals')
    op.drop_table('users')
