from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..board.model import BoardCard
from ..sprint.model import Sprint
from ..team.model import Team, TeamMembership
from ..user.model import User
from .schemas import (
    DashboardMemberRead,
    DashboardSprintRead,
    DashboardTaskRead,
    TeamDashboardRead,
)


async def get_team_dashboard(
    db: AsyncSession,
    team_uuid: str,
    user_uuid: str,
) -> TeamDashboardRead:
    """Build the aggregated dashboard for a team the user belongs to."""

    # Verify team exists and user is a member
    team_result = await db.execute(
        select(Team).where(Team.uuid == team_uuid, Team.deleted_at.is_(None))
    )
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    membership_result = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_uuid == team_uuid,
            TeamMembership.user_uuid == user_uuid,
            TeamMembership.deleted_at.is_(None),
        )
    )
    if not membership_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a team member")

    # Current sprint (most recent by starts_on)
    sprint_result = await db.execute(
        select(Sprint)
        .where(Sprint.team_uuid == team_uuid, Sprint.deleted_at.is_(None))
        .order_by(Sprint.starts_on.desc())
        .limit(1)
    )
    sprint = sprint_result.scalar_one_or_none()

    sprint_read = None
    tasks: list[DashboardTaskRead] = []
    total_tasks = 0
    done_tasks = 0
    progress_percent = 0

    if sprint:
        sprint_read = DashboardSprintRead(
            uuid=sprint.uuid,
            label=sprint.label,
            shared_goal=sprint.shared_goal,
            period_label=sprint.period_label,
            starts_on=sprint.starts_on,
            ends_on=sprint.ends_on,
        )

        # Board cards for this sprint
        cards_result = await db.execute(
            select(BoardCard, User.name)
            .outerjoin(User, BoardCard.assignee_user_uuid == User.uuid)
            .where(
                BoardCard.team_uuid == team_uuid,
                BoardCard.sprint_uuid == sprint.uuid,
                BoardCard.deleted_at.is_(None),
            )
            .order_by(BoardCard.position)
        )
        rows = cards_result.all()
        total_tasks = len(rows)
        done_tasks = sum(1 for card, _ in rows if card.column_key == "done")
        progress_percent = round(done_tasks * 100 / total_tasks) if total_tasks else 0

        tasks = [
            DashboardTaskRead(
                uuid=card.uuid,
                title=card.title,
                column_key=card.column_key,
                assignee_user_uuid=card.assignee_user_uuid,
                assignee_name=assignee_name,
            )
            for card, assignee_name in rows
        ]

    # Team members
    members_result = await db.execute(
        select(User.uuid, User.name, User.email, User.profile_image_url, TeamMembership.role)
        .join(TeamMembership, TeamMembership.user_uuid == User.uuid)
        .where(
            TeamMembership.team_uuid == team_uuid,
            TeamMembership.deleted_at.is_(None),
            User.deleted_at.is_(None),
        )
    )
    members = [
        DashboardMemberRead(
            user_uuid=row.uuid,
            name=row.name,
            email=row.email,
            profile_image_url=row.profile_image_url,
            role=row.role.value,
        )
        for row in members_result.all()
    ]

    return TeamDashboardRead(
        team_uuid=team.uuid,
        team_name=team.name,
        team_description=team.description,
        sprint=sprint_read,
        tasks=tasks,
        members=members,
        progress_percent=progress_percent,
        total_tasks=total_tasks,
        done_tasks=done_tasks,
    )
