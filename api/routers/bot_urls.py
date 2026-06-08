from fastapi import APIRouter, Query, Path, Depends

from api.schemas import Platform
from api.middlewares import require_permission
from api.utils import GameUtils
from api.apis.robot import BindAPI

router = APIRouter(prefix="/robot")


@router.get("/user/{platform}/{platform_uid}/binding/",summary="Root-Only Demo")
async def get_user_current_binding(
    _: str = Depends(require_permission("bot")),
    platform: Platform = Path(..., description="用户平台"),
    platform_uid: str = Path(..., description="用户平台UID"),

):
    platform_id = GameUtils.get_platform_id(platform)
    return await BindAPI.getCurrentBind(platform_id, platform_uid)
