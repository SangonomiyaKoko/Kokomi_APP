from typing import Optional
from fastapi import APIRouter, Query, Path, Depends

from api.middlewares import require_permission, AuthManager, MySQLManager
from api.response import JSONResponse
from api.utils import GameUtils
from api.schemas import Region
from api.apis.manager import TokenAPI, NodeAPI

router = APIRouter(prefix="/manager")


@router.get("/tokens/", summary="查询当前已加载的 API Token")
async def get_all_tokens(
    _: str = Depends(require_permission("root"))
):
    """【仅限 Root 权限用户】

    获取 API 中已加载的所有 token 的信息
    """
    return JSONResponse.success(AuthManager.get_tokens())


@router.post("/token/", summary="创建一个新的 API Token")
async def create_token(
    _: str = Depends(require_permission("root")),
    role_root: bool = Query(False, description="是否拥有 root 接口权限"),
    role_bot: bool = Query(False, description="是否拥有 bot 接口权限"),
    role_rank: bool = Query(False, description="是否拥有 rank 接口权限"),
    description: Optional[str] = Query(None, description="备注/描述")
):
    """【仅限 Root 权限用户】
    
    创建一个新的 API token，自动生成并返回一个 32 位 MD5 格式的 token 字符串
    """
    error, token = JSONResponse.extract_data(
        response=await TokenAPI.createToken(
            role_root=role_root,
            role_bot=role_bot,
            role_rank=role_rank,
            source=description
        )
    )
    if error:
        return token
    
    token_data = await MySQLManager.load_token()
    AuthManager.reload(token_data)

    return JSONResponse.success(token)


@router.delete("/token/{token}/", summary="删除指定的 API Token")
async def delete_token(
    _: str = Depends(require_permission("root")),
    token: str = Path(..., description="待删除 Token 值"),
):
    """【仅限 Root 权限用户】

    删除指定的 API token
    """
    error, token = JSONResponse.extract_data(
        response=await TokenAPI.deleteToken(token)
    )
    if error:
        return token
    
    token_data = await MySQLManager.load_token()
    AuthManager.reload(token_data)

    return JSONResponse.API_1000_Success


@router.put("/node/{region}/enable/", summary="启用子节点")
async def enable_node(
    _: str = Depends(require_permission("root")),
    region: Region = Path(..., description="节点")
):
    """【仅限 Root 权限用户】

    将指定子节点的 is_available 设置为 1（可用），并同步更新内存中的节点状态
    """
    region_id = GameUtils.get_region_id(region.value)
    return await NodeAPI.enableNode(region_id)


@router.put("/node/{region}/disable/", summary="禁用子节点")
async def disable_node(
    _: str = Depends(require_permission("root")),
    region: Region = Path(..., description="节点")
):
    """【仅限 Root 权限用户】

    将指定子节点的 is_available 设置为 0（不可用），并同步更新内存中的节点状态
    """
    region_id = GameUtils.get_region_id(region.value)
    return await NodeAPI.disableNode(region_id)
