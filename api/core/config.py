import os
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeConfig:
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

class EnvConfig:
    config = None
    LOG_DIR = Path('/app/logs')

    @classmethod
    def init(cls) -> str | None:
        # 加载config
        config = RuntimeConfig(
            MYSQL_HOST = os.getenv("MYSQL_HOST"),
            MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306)),
            MYSQL_USERNAME = os.getenv("MYSQL_USERNAME"),
            MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD"),
            MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
        )
        cls.config = config
        cls.LOG_DIR = Path(os.getenv("LOG_DIR"))
        return '.env'
