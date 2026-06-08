from fastapi import APIRouter, Query, Path, Depends

from api.schemas import Platform
from api.middlewares import require_permission
from api.schemas import Region
from api.utils import GameUtils
from api.apis.robot import BotBindAPI, UserRefreshAPI

router = APIRouter(prefix="/bot/platform")


@router.get("/user/{platform}/{platform_uid}/binding/",summary="读取平台用户的当前绑定账号")
async def get_user_current_binding(
    _: str = Depends(require_permission("bot")),
    platform: Platform = Path(..., description="用户平台"),
    platform_uid: str = Path(..., description="用户平台UID"),
):
    platform_id = GameUtils.get_platform_id(platform.value)
    return await BotBindAPI.getCurrentBind(platform_id, platform_uid)


@router.get("/account/{region}/{user_id}/",summary="刷新用户的缓存数据")
async def refreshUser(
    _: str = Depends(require_permission("bot")),
    region: Region = Path(..., description="服务器"),
    user_id: int = Path(..., description="用户ID")
):
    region_id = GameUtils.get_region_id(region.value)
    return await UserRefreshAPI.refresh_user(region_id, user_id)
