"""统计相关路由。"""

from fastapi import APIRouter, Depends
from app.services.stats_service import StatsService
from app.schemas.stats import StatsResponse
from app.api.deps import get_stats_service, require_admin
from app.models.user import User

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def get_overview(
    service: StatsService = Depends(get_stats_service),
    _current_user: User = Depends(require_admin),
):
    """获取全量统计概览（仅管理员）。"""
    return service.get_overview()
