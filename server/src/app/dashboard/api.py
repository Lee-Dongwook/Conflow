"""REST API for the team dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.verify_token import verify_token
from ..user.schemas import UserRead
from .schemas import TeamDashboardRead
from .service import get_team_dashboard

router = APIRouter(prefix="/teams", tags=["dashboard"])


@router.get("/{team_uuid}/dashboard", response_model=TeamDashboardRead)
async def team_dashboard(
    team_uuid: str,
    current_user: UserRead = Depends(verify_token),
    db: AsyncSession = Depends(get_async_db),
):
    """Aggregated dashboard for a team: sprint, tasks, members, progress."""
    return await get_team_dashboard(db, team_uuid, current_user.uuid)
