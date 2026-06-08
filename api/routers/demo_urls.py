from fastapi import APIRouter, Depends

from api.middlewares import require_permission
from api.response import JSONResponse

router = APIRouter(prefix="/demo")


@router.get("/root-only",summary="Root-Only Demo")
async def root_only_demo(
    _: str = Depends(require_permission("root")),
):
    """仅 root 权限 token 可访问的演示接口

    请求头 ``assess-token`` 必须携带具有 root 权限的有效 token，
    否则返回 403 权限不足。
    """
    return JSONResponse.API_1000_Success
