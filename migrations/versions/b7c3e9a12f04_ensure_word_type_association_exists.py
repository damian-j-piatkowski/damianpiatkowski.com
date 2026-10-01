"""ensure_word_type_association_exists

Revision ID: b7c3e9a12f04
Revises: fa9b2e01010f
Create Date: 2026-09-30 12:05:00.000000

Creates word_type_association when missing. The table was added to revision
fa9b2e01010f after that revision had already been applied on some databases,
so this follow-up migration repairs that drift idempotently.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'b7c3e9a12f04'
down_revision = 'fa9b2e01010f'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'word_type_association' not in existing_tables:
        op.create_table(
            'word_type_association',
            sa.Column('word_id', sa.Integer(), nullable=False),
            sa.Column('word_type', sa.String(length=32), nullable=False),
            sa.ForeignKeyConstraint(['word_id'], ['dictionary_words.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('word_id', 'word_type'),
        )


def downgrade():
    # Do not drop the table on downgrade: it may also have been created by
    # fa9b2e01010f on fresh installs, and removing it here would leave that
    # revision's upgrade path inconsistent.
    pass
