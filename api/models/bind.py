from typing import Optional

from api.constants import Limits
from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.middlewares import MySQLManager

class BotUserModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_current_bind(
        platform_id: int, 
        platform_uid: str,
        user_name: Optional[str] = None,
        user_avatar: Optional[str] = None
    ):
        """从数据库中读取用户的绑定的账号

        参数:
            platform_id: 平台 ID
            platform_uid: 用户 ID
        """
        async with MySQLManager.auto_transaction_cursor() as cur:
            sql = """
                SELECT 
                    id, 
                    binding_id 
                FROM T_user_info 
                WHERE platform_id = %s 
                  AND platform_uid = %s;
            """
            await cur.execute(sql, [platform_id, platform_uid])
            data = await cur.fetchone()
            if data is None:
                sql = """
                    INSERT INTO T_user_info (
                        platform_id, platform_uid, username, avatar
                    ) VALUES (
                        %s, %s, %s, %s
                    );
                """
                await cur.execute(sql, [
                    platform_id, platform_uid, user_name, user_avatar
                ])
                return JSONResponse.success({})
            elif data[1] is None:
                return JSONResponse.success({})
            else:
                sql = """
                    SELECT 
                        region_id, 
                        account_id, 
                        username, 
                        UNIX_TIMESTAMP(register_time) 
                    FROM T_user_base 
                    WHERE id = %s;
                """
                await cur.execute(sql, data[1])
                user = await cur.fetchone()
                if user is None:
                    return JSONResponse.success({})
                
                result = {
                    'region_id': user[0],
                    'account_id': user[1],
                    'username': user[2],
                    'created_at': user[3]
                }

                return JSONResponse.success(result)