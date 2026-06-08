import httpx
from typing import Optional

from api.core import api_logger
from api.schemas import NodeInfo


class NodeManager:
    """子节点连接管理器

    在内存中维护 region_id → NodeInfo 的映射，并持有共享的 httpx 连接池
    不与数据库直接交互 —— init() 的数据以及 httpx 客户端均由调用方传入
    """

    _nodes: dict[int, NodeInfo] = {}
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def init(
        cls,
        nodes_data: list[dict],
        client: httpx.AsyncClient,
    ) -> None:
        """初始化节点存储与连接池

        Args:
            nodes_data: T_node_info 全表查询结果，每行格式:
                {
                    "id": 1,
                    "host": "127.0.0.1",
                    "port": 8000,
                    "token": "root",
                    "is_available": 1,   # 0 或 1
                }
            client: 由调用方创建并传入的 httpx 异步连接池，
                    NodeManager 接管其生命周期，close() 时释放
        """
        cls._nodes.clear()
        for row in nodes_data:
            node = NodeInfo(
                id=row["id"],
                name=row["name"],
                host=row.get("host"),
                port=row.get("port"),
                token=row.get("token"),
                is_available=bool(row.get("is_available", 0))
            )
            cls._nodes[node.id] = node
        cls._client = client
        api_logger.info(f"NodeManager initialized: {len(cls._nodes)} nodes loaded")

    @classmethod
    def get_node(cls, region_id: int) -> Optional[NodeInfo]:
        """根据 region_id 获取可用节点信息

        满足以下任一条件时返回 None：
        - region_id 不在映射中（未配置）
        - is_available 为 False
        - host 或 token 未配置

        Args:
            region_id: D_region.id，即子节点编号

        Returns:
            可用的 NodeInfo；不可用或不存在时返回 None
        """
        node = cls._nodes.get(region_id)
        if node is None:
            return None
        if not node.is_available:
            return None
        if not node.host or not node.token:
            return None
        return node

    @classmethod
    def get_client(cls) -> Optional[httpx.AsyncClient]:
        """获取共享的 httpx 异步客户端

        供外部在需要对子节点发起 HTTP 请求时使用。

        Returns:
            httpx.AsyncClient 实例；未初始化时返回 None
        """
        return cls._client

    @classmethod
    def update_availability(cls, region_id: int, is_available: bool) -> bool:
        """DB 修改 is_available 后，同步更新内存中的状态

        Args:
            region_id: 子节点编号
            is_available: 新的可用状态

        Returns:
            True 表示更新成功；False 表示 region_id 不存在
        """
        node = cls._nodes.get(region_id)
        if node is None:
            return
        
        node.is_available = is_available
        api_logger.info(
            f"NodeStatus: region_id={region_id} is_available={is_available}"
        )

    @classmethod
    async def close(cls) -> None:
        """释放 httpx 连接池资源

        应在应用 shutdown 阶段调用。
        """
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
            api_logger.info("NodeManager: httpx client closed")
