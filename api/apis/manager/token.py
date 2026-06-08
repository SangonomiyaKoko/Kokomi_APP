from typing import Optional

from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.models import TokenModel


class TokenAPI:
    @ExceptionLogger.handle_program_exception_async
    async def getTokens():
        """获取所有 API token 列表"""
        return await TokenModel.get_all_tokens()

    @ExceptionLogger.handle_program_exception_async
    async def createToken(
        role_root: bool = False,
        role_bot: bool = False,
        role_rank: bool = False,
        source: Optional[str] = None
    ):
        """创建新的 API token"""
        return await TokenModel.create_token(
            role_root=role_root,
            role_bot=role_bot,
            role_rank=role_rank,
            source=source
        )

    @ExceptionLogger.handle_program_exception_async
    async def deleteToken(token: str):
        """删除指定 token"""
        return await TokenModel.delete_token(token)
