import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class MySQLConfig:
    """MySQL 数据库配置"""
    host: str
    port: int
    user: str
    password: str
    db: str

@dataclass(frozen=True)
class RedisConfig:
    """Redis 配置"""
    host: str
    port: int
    password: str
    db: str
    protocol: str

@dataclass(frozen=True)
class RuntimeConfig:
    MYSQL: MySQLConfig
    REDIS: RedisConfig

class EnvConfig:
    PLATFORM: Optional[str] = None

    ROOT_DIR: Path = Path('/app')
    LOG_DIR: Path = Path('/app/logs')

    _config: Optional[RuntimeConfig] = None

    @classmethod
    def _require_env(cls, key: str, default: Optional[str] = None) -> str:
        """获取环境变量"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    @classmethod
    def _load_env_file(cls) -> str:
        """加载环境变量文件，返回环境文件名"""
        # 判断是否在 Docker 环境：PLATFORM 环境变量由 Docker 容器注入
        if os.getenv('PLATFORM') is None:
            # Windows 本地开发，需要手动从文件加载环境变量
            from dotenv import load_dotenv
            if not load_dotenv('.env'):
                raise RuntimeError("Failed to load .env file")
            return '.env'
        # Docker 容器环境，环境变量已通过容器编排工具注入
        # 直接使用 os.getenv() 即可读取，无需加载文件
        return '.env'

    @classmethod
    def _init_runtime_config(cls):
        """初始化运行时配置"""
        cls.PLATFORM=cls._require_env('PLATFORM')

        cls._config = RuntimeConfig(
            MYSQL=MySQLConfig(
                host=cls._require_env("MYSQL_HOST"),
                port=int(cls._require_env("MYSQL_PORT", "3306")),
                user='root',  # 默认使用 root 用户
                password=cls._require_env("MYSQL_ROOT_PASSWORD"),  # 加载 root 用户密码
                db=cls._require_env("MYSQL_DATABASE")
            ),
            REDIS=RedisConfig(
                host=cls._require_env("REDIS_HOST"),
                port=int(cls._require_env("REDIS_PORT", "6379")),
                password=cls._require_env("REDIS_PASSWORD"),
                db=int(cls._require_env("REDIS_DATABASE", "0")),
                protocol=int(cls._require_env("REDIS_PROTOCOL", "0"))
            )
        )

    @classmethod
    def init(cls, root_path: str) -> str:
        """
        初始化所有配置
        返回当前使用的环境文件名 (`env.dev` 或 `env.prod`)
        """
        # 加载文件路径
        cls.ROOT_DIR = Path(root_path)
        cls.LOG_DIR = cls.ROOT_DIR / 'logs'
        # 加载环境变量文件
        env_file = cls._load_env_file()
        # 初始化运行配置
        cls._init_runtime_config()

        return env_file

    @classmethod
    def get_config(cls) -> RuntimeConfig:
        """获取运行时配置，如果未初始化则抛出异常"""
        if cls._config is None:
            raise RuntimeError("Configuration not initialized")
        return cls._config