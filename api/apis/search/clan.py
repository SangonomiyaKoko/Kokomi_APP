from api.response import JSONResponse
from api.loggers import ExceptionLogger
from api.network.api import NodeAPI
from api.network.node import NodeManager


class ClanSearchAPI:
    @ExceptionLogger.handle_program_exception_async
    async def search(
        region_id: int, 
        tag: str
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = f"/api/platform/search/clan/"
        params = {
            'tag': tag
        }
        response = await NodeAPI.get(node, path, params)

        return response