import json
from typing import Optional
import redis.asyncio as redis
from redis.asyncio.client import Redis

from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.core import EnvConfig, api_logger


class RedisConnection:
    '''管理Redis连接'''
    _conn: Optional[Redis] = None

    @staticmethod
    def _build_redis_url() -> str:
        """构建Redis连接URL"""
        config = EnvConfig.get_config()
        return (
            f"redis://:{config.REDIS.password}"
            f"@{config.REDIS.host}"
            f":{config.REDIS.port}"
            f"/{config.REDIS.db}"
        )

    @classmethod
    async def init_conn(cls) -> Redis:
        """应用启动时调用，初始化Redis连接"""
        try:
            redis_url = cls._build_redis_url()
            cls._conn = redis.from_url(
                url=redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            api_logger.info("Redis connection initialized successfully")
        except Exception as e:
            api_logger.error(f"Failed to initialize Redis connection: {e}")
            raise

    @classmethod
    async def test_redis(cls) -> None:
        """测试Redis连接"""
        try:
            conn = cls.acquire_conn()
            ping_response = await conn.ping()
            if ping_response:
                info = await conn.info("server") # type: dict
                api_logger.info(f"Redis version: {info.get('redis_version', 'unknown')}")
                api_logger.info(f"Redis mode: {info.get('redis_mode', 'unknown').upper()}")
            else:
                api_logger.warning(f"Redis ping failed: {ping_response}")
        except Exception as e:
            api_logger.warning(f"Test Redis connection failed: {e}")

    @classmethod
    async def close_redis(cls) -> None:
        """关闭Redis连接"""
        if cls._conn is None:
            api_logger.info("Redis connection is already closed or not initialized")
            return
        
        try:
            await cls._conn.close()
            api_logger.info("Redis connection closed")
        except Exception as e:
            api_logger.error(f"Failed to close Redis connection: {e}")
        finally:
            cls._conn = None

    @classmethod
    def acquire_conn(cls) -> Redis:
        """获取Redis连接"""
        if cls._conn is None:
            raise RuntimeError("Redis connection is not initialized")
        return cls._conn
        
class RedisClient:
    @staticmethod
    @ExceptionLogger.handle_cache_exception_async
    async def get(key: str) -> dict:
        conn = RedisConnection.acquire_conn()
        data = await conn.get(key)
        if data:
            data = json.loads(data)
        return JSONResponse.success(data)
    
    @staticmethod
    @ExceptionLogger.handle_cache_exception_async
    async def drop(key: str) -> dict:
        conn = RedisConnection.acquire_conn()
        await conn.delete(key)
        return JSONResponse.API_1000_Success
    
    @staticmethod
    @ExceptionLogger.handle_cache_exception_async
    async def api_record(date: str) -> None:
        """记录一次 API 请求"""
        try:
            conn = RedisConnection.acquire_conn()
        except RuntimeError:
            return
        
        await conn.incr(f'api:daily:{date}')
        await conn.incr(f'api:monthly:{date[:7]}')
        await conn.incr(f'api:annual:{date}[:4]')
    
    @staticmethod
    @ExceptionLogger.handle_cache_exception_async
    async def exists(key: str) -> dict:
        conn = RedisConnection.acquire_conn()
        data = await conn.exists(key)
        return JSONResponse.success(data)

    @staticmethod
    @ExceptionLogger.handle_cache_exception_async
    async def set(key: str, value: dict, ex: int = None):
        conn = RedisConnection.acquire_conn()
        await conn.set(
            name=key, 
            value=json.dumps(value, ensure_ascii=False),
            ex=ex
        )
        return JSONResponse.API_1000_Success