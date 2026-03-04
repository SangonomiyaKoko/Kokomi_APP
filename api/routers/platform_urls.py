from fastapi import APIRouter

from api.apis.platform import (
    RefreshAPI
)

router = APIRouter()

@router.put("/refresh/config/", summary="刷新配置参数")
async def searchUser():
    return await RefreshAPI.refreshConfig()