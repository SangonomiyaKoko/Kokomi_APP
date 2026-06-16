from datetime import datetime, timezone


class TimeUtils:
    """时间相关工具函数集合"""
    def timestamp() -> int:
        """获取当前 UTC 时间戳（秒）"""
        return int(datetime.now(timezone.utc).timestamp())

    def timestamp_ms() -> int:
        """获取当前 UTC 时间戳（毫秒）"""
        return int(datetime.now(timezone.utc).timestamp() * 1000)
    
    def diff_timestamp(timestamp: int) -> int:
        """获取传入时间戳和当前时间的差值"""
        if timestamp is None:
            return None
        
        return int(datetime.now(timezone.utc).timestamp() - timestamp)
    
    def now_iso() -> str:
        """获取指定时区的当前时间（ISO 8601 格式，默认 UTC 时区）"""
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    
    def offset_iso(offset: int = 0, strftime: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取指定时区的当前时间（ISO 8601 格式，默认 UTC 时区）"""
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        timestamp = current_timestamp - offset * 86400
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(strftime)
    
    def fromtimestamp(timestamp: int, strftime: str = "%Y-%m-%d %H:%M:%S"):
        """
        获取指定时间戳的UTC时间（默认 %Y-%m-%d %H:%M:%S 格式）
        """
        if timestamp is None:
            return None

        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(strftime)
