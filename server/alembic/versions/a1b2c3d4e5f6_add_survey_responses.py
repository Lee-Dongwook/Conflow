"""add survey_responses table

Revision ID: a1b2c3d4e5f6
Revises: e6751c3c016c
Create Date: 2026-06-13 18:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str | Sequence[str] | None = 'e6751c3c016c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'survey_responses',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('survey_key', sa.String(length=64), nullable=False),
        sa.Column('respondent_role', sa.String(length=50), nullable=False),
        sa.Column('organization', sa.String(length=200), nullable=True),
        sa.Column('contact_email', sa.String(length=200), nullable=True),
        sa.Column('consents_to_followup', sa.Boolean(), nullable=False),
        sa.Column('answers', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_index(
        'ix_survey_responses_survey_key',
        'survey_responses',
        ['survey_key'],
        unique=False,
    )
    op.create_index(
        'ix_survey_responses_respondent_role',
        'survey_responses',
        ['respondent_role'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_survey_responses_respondent_role', table_name='survey_responses')
    op.drop_index('ix_survey_responses_survey_key', table_name='survey_responses')
    op.drop_table('survey_responses')
