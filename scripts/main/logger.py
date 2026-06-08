import sys
import logging
from pathlib import Path

from settings import (
    LOG_DIR,
    DATE_FMT,
    CLIENT_NAME
)


class CustomLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(name, level)
        self._console_handler = None
        self._file_handler = None

    def set_handlers(self, console_handler: logging.StreamHandler, file_handler: logging.FileHandler):
        """设置 handlers（在初始化完成后调用）"""
        self._console_handler = console_handler
        self._file_handler = file_handler
        self.addHandler(console_handler)
        self.addHandler(file_handler)


def _create_console_handler(level: int) -> logging.StreamHandler:
    """创建控制台 handler（输出所有 level 及以上日志）"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)  # DEBUG 或 INFO
    handler.setFormatter(logging.Formatter(
        f'%(asctime)s [%(levelname)s] %(message)s',
        datefmt=DATE_FMT
    ))
    return handler


def _create_file_handler() -> logging.FileHandler:
    """创建文件 handler（只记录 WARNING 及以上）"""
    log_path = Path(LOG_DIR) / 'scripts' / f'{CLIENT_NAME}.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    handler.setLevel(logging.WARNING)  # 只记录 WARNING 及以上
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt=DATE_FMT
    ))
    return handler


def init_logger(console_level: int = logging.INFO) -> CustomLogger:
    """初始化 logger
    Args:
        console_level: 控制台输出级别（DEBUG 或 INFO）
    """
    # 保存原 logger 类并设置自定义类
    old_class = logging.getLoggerClass()
    logging.setLoggerClass(CustomLogger)
    
    # 获取或创建 logger
    logger = logging.getLogger(CLIENT_NAME)
    
    # 恢复默认类
    logging.setLoggerClass(old_class)
    
    # 清除已有的 handlers（避免重复）
    if logger.handlers:
        logger.handlers.clear()
    
    # 设置 logger 级别为最低（DEBUG），让 handler 自己控制
    logger.setLevel(logging.DEBUG)
    
    # 创建 handlers
    console_handler = _create_console_handler(console_level)
    file_handler = _create_file_handler()  # 内部已设置 WARNING 级别
    
    # 设置 handlers 到 logger
    logger.set_handlers(console_handler, file_handler)
    
    # 防止日志传播到 root logger
    logger.propagate = False
    
    return logger


# 初始化
logger = init_logger(console_level=logging.INFO)