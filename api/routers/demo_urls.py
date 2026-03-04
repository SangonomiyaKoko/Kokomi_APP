from fastapi import APIRouter, Query, Path

from api.schemas import Region
from api.response import JSONResponse
from api.utils import GameUtils
from api.apis.demo import (
    TestAPI
)

router = APIRouter()

@router.get("/test/error/", summary="测试错误日志功能")
async def testErrorLog():
    return await TestAPI.test_error_log()