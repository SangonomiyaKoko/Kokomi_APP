from api.response import JSONResponse
from api.loggers import ExceptionLogger
from api.network.api import NodeAPI
from api.network.node import NodeManager


class BotRankingAPI:
    @ExceptionLogger.handle_program_exception_async
    async def get_ship_top(
        region_id: int, 
        ship_id: int,
        language: str = 'zh_sg'
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = f"/api/ranking/ship/{ship_id}/external/"
        params = {
            'page': 1,
            'size': 50,
            'language': language
        }
        response = await NodeAPI.get(node, path, params)

        return response