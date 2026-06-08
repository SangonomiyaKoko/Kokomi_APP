from datetime import datetime, timezone


class TimeUtils:
    """时间相关工具函数集合"""
    @staticmethod
    def timestamp() -> int:
        """
        获取当前 UTC 时间戳（秒）
        """
        return int(datetime.now(timezone.utc).timestamp())

    @staticmethod
    def timestamp_ms() -> int:
        """
        获取当前 UTC 时间戳（毫秒）
        """
        return int(datetime.now(timezone.utc).timestamp() * 1000)
    
    def now_iso() -> str:
        """
        获取指定时区的当前时间（ISO 8601 格式，默认当前时区）
        """
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    
    def fromtimestamp(timestamp: int, strftime: str = "%Y-%m-%d %H:%M:%S"):
        """
        获取指定时间戳的UTC时间（默认 %Y-%m-%d %H:%M:%S 格式）
        """
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(strftime)
