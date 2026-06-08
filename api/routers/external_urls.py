from fastapi import APIRouter, Depends, Path, Query

from api.middlewares import require_permission
from api.schemas import Region
from api.utils import GameUtils
from api.apis.external import ExternalRankingAPI, ExternalStatsAPI

router = APIRouter(prefix="/external")


@router.get("/ship-ranking/{region}/{ship_id}/",summary="服务器船只排行榜")
async def getShipTop(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器"),
    ship_id: int = Path(..., description="船只ID"),
    page_index: int = Query(1, description="页索引"),
    page_size: int = Query(50, description="页大小"),
    dogtag: int = Query(0, description="页大小")
):
    region_id = GameUtils.get_region_id(region.value)
    return await ExternalRankingAPI.get_ship_top(region_id, ship_id, page_index, page_size, dogtag)


@router.get("/user-refresh/{region}/{user_id}/",summary="刷洗用户缓存数据")
async def refreshUser(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器"),
    user_id: int = Path(..., description="用户ID")
):
    region_id = GameUtils.get_region_id(region.value)
    return await ExternalRankingAPI.refresh_user(region_id, user_id)


@router.get("/ship-stats/{region}/",summary="获取船只的服务器数据")
async def getShipStats(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器")
):
    region_id = GameUtils.get_region_id(region.value)
    return await ExternalStatsAPI.get_ship_stats(region_id)