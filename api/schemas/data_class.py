from dataclasses import dataclass
from typing import Optional


@dataclass
class NodeInfo:
    """子节点连接信息

    与 T_node_info 表行一一对应。
    """
    id: int                    # D_region.id
    name: str                  # D_region.name
    host: Optional[str]        # 节点 IP / 域名
    port: Optional[int]        # 节点端口
    token: Optional[str]       # 节点鉴权 token
    is_available: bool         # 是否可用（映射 TINYINT: 0→False, 1→True）