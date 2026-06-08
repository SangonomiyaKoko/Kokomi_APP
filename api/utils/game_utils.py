from api.core import EnvConfig


class GameUtils:
    """存放和游戏相关的工具函数"""
    def get_region_id(region: str) -> int:
        region_id = {
            'asia': 1,
            'eu': 2,
            'na': 3,
            'ru': 4,
            'cn': 5
        }.get(region, 1)

        return region_id
    
    def get_platform_id(platform: str) -> int:
        platform_id = {
            'qq_bot': 1,
            'qq_group': 2,
            'qq_guild': 3,
            'discord': 4
        }.get(platform, 1)

        return platform_id