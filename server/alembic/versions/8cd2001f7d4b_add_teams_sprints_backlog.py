"""add teams sprints backlog

Revision ID: 8cd2001f7d4b
Revises: dd8ba2808f86
Create Date: 2026-05-10 10:17:29.154658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8cd2001f7d4b'
down_revision: Union[str, Sequence[str], None] = 'dd8ba2808f86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    # PostgreSQL: ENUM types must exist before columns reference them.
    # Labels match Python Enum .value in models (not member names).
    userrole = postgresql.ENUM('admin', 'user', name='userrole')
    userrole.create(bind, checkfirst=True)

    teammemberrole = postgresql.ENUM('owner', 'admin', 'member', name='teammemberrole')
    teammemberrole.create(bind, checkfirst=True)

    backlog_priority_t = postgresql.ENUM(
        'low', 'medium', 'high', 'critical', name='backlog_priority'
    )
    backlog_priority_t.create(bind, checkfirst=True)

    userrole_col = postgresql.ENUM(
        'admin', 'user', name='userrole', create_type=False
    )
    teammemberrole_col = postgresql.ENUM(
        'owner', 'admin', 'member', name='teammemberrole', create_type=False
    )
    backlog_priority_col = postgresql.ENUM(
        'low', 'medium', 'high', 'critical', name='backlog_priority', create_type=False
    )

    op.create_table(
        'common_resources',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('user_uuid', sa.UUID(as_uuid=False), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_index(
        'idx_common_resources_user_uuid',
        'common_resources',
        ['user_uuid'],
        unique=False,
    )
    op.create_table(
        'teams',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_table(
        'sprints',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('team_uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('label', sa.String(length=128), nullable=False),
        sa.Column('starts_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('shared_goal', sa.String(length=256), nullable=True),
        sa.Column('period_label', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['team_uuid'], ['teams.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_table(
        'team_memberships',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('team_uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('role', teammemberrole_col, nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['team_uuid'], ['teams.uuid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('uuid'),
        sa.UniqueConstraint('user_uuid', 'team_uuid', name='uq_team_membership_user_team'),
    )
    op.create_table(
        'backlog_items',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('team_uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('sprint_uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('assignee_user_uuid', sa.UUID(as_uuid=False), nullable=True),
        sa.Column('priority', backlog_priority_col, nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['assignee_user_uuid'], ['users.uuid'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sprint_uuid'], ['sprints.uuid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_uuid'], ['teams.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_table(
        'sprint_metric_snapshots',
        sa.Column('uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sprint_uuid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('week_label', sa.String(length=64), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['sprint_uuid'], ['sprints.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('uuid'),
    )

    op.add_column(
        'users',
        sa.Column(
            'role',
            userrole_col,
            nullable=False,
            server_default=sa.text("'user'::userrole"),
        ),
    )
    op.alter_column('users', 'role', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    op.drop_column('users', 'role')

    userrole = postgresql.ENUM('admin', 'user', name='userrole')
    userrole.drop(bind, checkfirst=True)

    op.drop_table('sprint_metric_snapshots')
    op.drop_table('backlog_items')

    backlog_priority_t = postgresql.ENUM(
        'low', 'medium', 'high', 'critical', name='backlog_priority'
    )
    backlog_priority_t.drop(bind, checkfirst=True)

    op.drop_table('team_memberships')

    teammemberrole = postgresql.ENUM('owner', 'admin', 'member', name='teammemberrole')
    teammemberrole.drop(bind, checkfirst=True)

    op.drop_table('sprints')
    op.drop_table('teams')
    op.drop_index('idx_common_resources_user_uuid', table_name='common_resources')
    op.drop_table('common_resources')

