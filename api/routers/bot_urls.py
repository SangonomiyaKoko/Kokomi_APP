from fastapi import APIRouter, Query, Path

from api.response import JSONResponse
from api.apis.robot import BindAPI, TokenAPI
from api.schemas import Platform, BindBody, BindIndex
from api.utils import GameUtils, StringUtils

router = APIRouter()

@router.post("/users/{platform}/{user_id}/bindings/", summary="通过uid/ign绑定")
async def getBind(body: BindBody, platform: Platform = Path(...), user_id: str = Path(...)):
    if body.type == 'ign':
        if not 3 <= len(body.ign) <= 25:
            return JSONResponse.API_2002_IllegalUserName
    else:
        if GameUtils.check_aid_and_rid(body.region, body.uid) == False:
            return JSONResponse.API_2007_IllegalAccoutID
    return await BindAPI.postBind(platform, user_id, body)

@router.get("/users/{platform}/{user_id}/", summary="查询用户数据")
async def getBind(platform: Platform = Path(...), user_id: str = Path(...)):
    return await BindAPI.getUser(platform, user_id)

@router.get("/users/{platform}/{user_id}/accounts/", summary="查询绑定数据")
async def getBind(platform: Platform = Path(...), user_id: str = Path(...)):
    return await BindAPI.getBind(platform, user_id)

@router.get("/users/{platform}/{user_id}/accounts/list/", summary="查询绑定列表数据")
async def getBind(platform: Platform = Path(...), user_id: str = Path(...)):
    return await BindAPI.getBindList(platform, user_id)

@router.delete("/users/{platform}/{user_id}/accounts/", summary="删除指定绑定")
async def delBind(platform: Platform = Path(...), user_id: str = Path(...), index: BindIndex = Query(BindIndex.IDX1)):
    return await BindAPI.delBind(platform, user_id, index)

@router.patch("/users/{platform}/{user_id}/accounts/", summary="切换绑定")
async def switchBind(platform: Platform = Path(...), user_id: str = Path(...), index: BindIndex = Query(BindIndex.IDX1)):
    return await BindAPI.switchBind(platform, user_id, index)