from enum import Enum

class Region(str, Enum):
    ASIA = "asia"
    EU = "eu"
    NA = "na"
    RU = "ru"
    CN = "cn"

class Server(str, Enum):
    WG = 'wg'
    LESTA = 'lesta'

class Platform(str, Enum):
    QQ_BOT = 'qq_bot'
    QQ_GROUP = 'qq_group'
    QQ_GUILD = 'qq_guild'
    DISCORD = 'discord'

class Language(str, Enum):
    ZH_SG = 'zh_sg'
    ZH_CN = 'zh_cn'
    EN = 'en'