from api.loggers import ExceptionLogger
from api.middlewares import RedisClient
from api.response import JSONResponse
from api.models import BotUserModel
from api.utils import GameUtils


class BindAPI:
    @staticmethod
    @ExceptionLogger.handle_program_exception_async
    async def getCurrentBind(platform_id: int, user_id: str):
        platform_uid = str(platform_id) + user_id
        redis_key = f"bot_bind:{platform_uid}"
        error, user_bind = JSONResponse.extract_data(
            response=await RedisClient.get(redis_key)
        )
        if error:
            return user_bind
        
        if user_bind:
            return JSONResponse.success(user_bind)
        
        error, user_bind = JSONResponse.extract_data(
            response=await BotUserModel.get_current_bind(platform_id, user_id)
        )
        if error:
            return user_bind
        
        if user_bind == {}:
            return JSONResponse.API_1000_Success
        
        result = {
            'region_id': user_bind['region_id'],
            'account_id': user_bind['account_id']
        }
        await RedisClient.set(redis_key, result)

        return JSONResponse.success(result)