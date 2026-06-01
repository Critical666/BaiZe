"""统计相关路由。"""

from fastapi import APIRouter, Depends
from app.services.stats_service import StatsService
from app.api.deps import get_stats_service

router = APIRouter()


@router.get("/stats")
def get_overview(service: StatsService = Depends(get_stats_service)):
    """获取全量统计概览。"""
    return service.get_overview()
