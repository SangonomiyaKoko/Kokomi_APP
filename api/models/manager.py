import uuid
import hashlib
from typing import Optional

from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.middlewares import MySQLManager


class NodeModel:
    @ExceptionLogger.handle_database_exception_async
    async def set_node_availability(node_id: int, is_available: bool):
        """设置子节点的可用状态

        Args:
            node_id: 子节点编号 (D_region.id)
            is_available: True=可用, False=不可用
        """
        async with MySQLManager.auto_transaction_cursor() as cur:
            sql = "UPDATE T_node_info SET is_available = %s WHERE id = %s;"
            await cur.execute(sql, [int(is_available), node_id])

        return JSONResponse.API_1000_Success


class TokenModel:
    @staticmethod
    def _generate_token() -> str:
        """生成一个 32 位 MD5 格式的 token"""
        return hashlib.md5(uuid.uuid4().bytes).hexdigest()

    @ExceptionLogger.handle_database_exception_async
    async def create_token(
        role_root: bool = False,
        role_bot: bool = False,
        role_rank: bool = False,
        source: Optional[str] = None
    ):
        """创建一个新的 API token

        自动生成 token 字符串并写入数据库。

        Args:
            role_root: 是否授予 root 权限
            role_bot: 是否授予 bot 权限
            role_rank: 是否授予 rank 权限
            source: token 来源/用途描述
        """
        token = TokenModel._generate_token()

        async with MySQLManager.auto_transaction_cursor() as cur:
            sql = """
                INSERT INTO T_api_token (
                    token, role_root, role_bot, role_rank, source
                ) VALUES (
                    %s, %s, %s, %s, %s
                );
            """
            await cur.execute(sql, [
                token, role_root, role_bot, role_rank, source
            ])

            return JSONResponse.success(token)

    @ExceptionLogger.handle_database_exception_async
    async def delete_token(token: str):
        """删除指定 token

        Args:
            token: 值
        """
        async with MySQLManager.auto_transaction_cursor() as cur:
            sql = "DELETE FROM T_api_token WHERE token = %s;"
            await cur.execute(sql, [token])

        return JSONResponse.API_1000_Success
