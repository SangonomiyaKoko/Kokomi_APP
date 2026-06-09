from typing import Optional

from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.middlewares import MySQLManager

class AccountModel:
    @ExceptionLogger.handle_database_exception_async
    async def refresh_account_base(
        region_id: int, 
        account_id: str,
        user_name: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        """刷新用户的基本信息"""
        async with MySQLManager.auto_transaction_cursor() as cur:
            sql = """
                SELECT id
                FROM T_user_base 
                WHERE region_id = %s 
                  AND account_id = %s;
            """
            await cur.execute(sql, [region_id, account_id])
            data = await cur.fetchone()
            if data is None:
                sql = """
                    INSERT INTO T_user_base (
                        region_id, account_id, username, register_time
                    ) VALUES (
                        %s, %s, %s, FROM_UNIXTIME(%s)
                    );
                """
                await cur.execute(sql, [
                    region_id, account_id, user_name, created_at
                ])
                return JSONResponse.API_1000_Success
            else:
                sql = """
                    UPDATE T_user_base 
                    SET 
                        username = %s,
                        register_time = FROM_UNIXTIME(%s)
                    WHERE region_id = %s 
                      AND account_id = %s;
                """
                await cur.execute(sql, [
                    user_name, created_at, region_id, account_id
                ])
                return JSONResponse.API_1000_Success