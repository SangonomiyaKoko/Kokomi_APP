from api.core import api_logger
from api.middlewares import RedisClient

async def server_check():
    for server_name in ['SchedulerUser', 'SchedulerClan']:
        redis_key = f"status:{server_name}"
        result = await RedisClient.exists(redis_key)
        if result['data'] != 1:
            # 服务离线
            api_logger.warning(f"{server_name} Server offline.")
        else:
            # 服务正常
            api_logger.info(f"{server_name} Server running.")