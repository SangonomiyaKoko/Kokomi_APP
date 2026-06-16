from fastapi import APIRouter, Depends, Path, Query

from api.middlewares import require_permission
from api.schemas import Region
from api.utils import GameUtils
from api.apis.external import ExternalStatsAPI

router = APIRouter(prefix="/external")


@router.get("/ship-stats/{region}/",summary="获取船只的服务器数据")
async def getShipStats(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器")
):
    """获取指定服务器下船只的服务器数据

    该数据为船只的场次平均数据而非用户平均数据，仅返回有数据的船只
    """
    region_id = GameUtils.get_region_id(region.value)

    return await ExternalStatsAPI.get_ship_stats(region_id)