from fastapi import APIRouter, Depends, Path, Query

from api.middlewares import require_permission
from api.schemas import Region, Language, RankingRegion
from api.utils import GameUtils
from api.apis.ranking import ShipRankingAPI, ClanRankingAPI, UserRankingAPI, UserRefreshAPI


router = APIRouter(prefix="/bot/ranking")


@router.get("/account/{region}/{user_id}/",summary="刷新用户的缓存数据")
async def refreshUser(
    _: str = Depends(require_permission("bot")),
    region: Region = Path(..., description="服务器"),
    user_id: int = Path(..., description="用户ID")
):
    region_id = GameUtils.get_region_id(region.value)
    return await UserRefreshAPI.refresh_user(region_id, user_id)


@router.get("/ship/top50/{region}/{ship_id}/",summary="服务器船只排行榜 TOP 50")
async def getShipTop(
    _: str = Depends(require_permission("bot")),
    region: RankingRegion = Path(..., description="服务器"),
    ship_id: int = Path(..., description="船只ID"),
    language: Language = Query(Language.ZH_SG, description="语言")
):
    """返回服务器船只排行榜 TOP 50

    本接口 Credits 消耗: 5
    """
    credits_spent = 5
    region_id = GameUtils.get_region_id(region.value)

    return await ShipRankingAPI.get_ship_ranking(
        credits=credits_spent,
        region_id=region_id, 
        ship_id=ship_id, 
        language=language.value
    )


@router.get("/clan/top50/{region}/{ship_id}/",summary="服务器工会排行榜 TOP 50")
async def getShipTop(
    _: str = Depends(require_permission("bot")),
    region: RankingRegion = Path(..., description="服务器")
):
    """返回服务器工会排行榜 TOP 50

    本接口 Credits 消耗: 2
    """
    credits_spent = 2
    region_id = GameUtils.get_region_id(region.value)

    return await ClanRankingAPI.get_clan_ranking(
        credits=credits_spent,
        region_id=region_id
    )


@router.get("/user/top50/{region}/{user_id}/",summary="用户上榜船只统计")
async def getShipTop(
    _: str = Depends(require_permission("bot")),
    region: Region = Path(..., description="服务器"),
    user_id: int = Path(..., description="用户ID"),
    language: Language = Query(Language.ZH_SG, description="语言")
):
    """返回用户进入所在服务器船只 TOP50 的所有船只及排行信息

    本接口 Credits 消耗: 8
    """
    credits_spent = 8
    region_id = GameUtils.get_region_id(region.value)

    return await UserRankingAPI.get_user_ranking(
        credits=credits_spent,
        region_id=region_id, 
        user_id=user_id, 
        language=language.value
    )