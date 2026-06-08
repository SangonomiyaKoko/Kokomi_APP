from fastapi import APIRouter, Depends, Path, Query

from api.middlewares import require_permission
from api.schemas import Region, Language
from api.utils import GameUtils
from api.apis.ranking import ShipRankingAPI

router = APIRouter(prefix="/bot/ranking")


@router.get("/ship/{region}/{ship_id}/",summary="服务器船只排行榜")
async def getShipTop(
    _: str = Depends(require_permission("bot")),
    region: Region = Path(..., description="服务器"),
    ship_id: int = Path(..., description="船只ID"),
    language: Language = Query(Language.ZH_SG, description="语言")
):
    region_id = GameUtils.get_region_id(region.value)
    return await ShipRankingAPI.get_ship_top50(region_id, ship_id, language.value)