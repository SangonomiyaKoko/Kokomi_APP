from fastapi import APIRouter, Depends, Path, Query

from api.middlewares import require_permission
from api.schemas import Region
from api.utils import GameUtils
from api.apis.search import UserSearchAPI, ClanSearchAPI


router = APIRouter(prefix="/bot/search")


@router.get("/user/{region}/{name}/",summary="通过名称查找用户")
async def getShipTop(
    _: str = Depends(require_permission("bot")),
    region: Region = Path(..., description="服务器"),
    name: str = Path(..., description="用户名称")
):
    region_id = GameUtils.get_region_id(region.value)
    return await UserSearchAPI.search(region_id, name)


@router.get("/clan/{region}/{tag}/",summary="通过名称查找工会")
async def getShipTop(
    _: str = Depends(require_permission("bot")),
    region: Region = Path(..., description="服务器"),
    tag: str = Path(..., description="工会名称")
):
    region_id = GameUtils.get_region_id(region.value)
    return await ClanSearchAPI.search(region_id, tag)