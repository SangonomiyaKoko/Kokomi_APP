from api.response import JSONResponse
from api.loggers import ExceptionLogger
from api.network.api import NodeAPI
from api.network.node import NodeManager


class ExternalRankingAPI:
    @ExceptionLogger.handle_program_exception_async
    async def get_ship_top(
        region_id: int, 
        ship_id: int,
        page_index: int,
        page_size: int,
        dogtag: int = 0
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = f"/api/ranking/ship/{ship_id}/external/"
        params = {
            'page': page_index,
            'size': page_size,
            'dogtag': dogtag
        }
        response = await NodeAPI.get(node, path, params)

        return response
    
    @ExceptionLogger.handle_program_exception_async
    async def refresh_user(
        region_id: int, 
        user_id: int
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = f"/api/platform/user/{user_id}/"
        params = {}
        response = await NodeAPI.patch(node, path, params)

        # 检查子节点响应是否成功
        error, data = JSONResponse.extract_data(response)
        if error:
            return response

        return JSONResponse.API_1000_Success
    
    @ExceptionLogger.handle_program_exception_async
    async def get_ship_stats(
        region_id: int
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = "/api/maintenance/ship/stats/"
        params = {}
        response = await NodeAPI.get(node, path, params)

        # 检查子节点响应是否成功
        error, data = JSONResponse.extract_data(response)
        if error:
            return response
        
        result = []

        for ship_id, ship_data in data.items():
            result.append({
                'ship_id': int(ship_id),
                'battles': ship_data[0],
                'win_rate': ship_data[1],
                'avg_damage': ship_data[2],
                'avg_frags': ship_data[3]
            })

        return JSONResponse.success(result)