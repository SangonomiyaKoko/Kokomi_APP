from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.models import NodeModel
from api.network import NodeManager


class NodeAPI:
    @ExceptionLogger.handle_program_exception_async
    async def enableNode(node_id: int):
        """启用子节点"""
        node = NodeManager.get_node(node_id)
        
        path = f"/api/maintenance/state/"
        params = {
            "available": True
        }
        error, update = JSONResponse.extract_data(
            response=await NodeAPI.patch(node, path, params)
        )
        if error:
            return update

        error, update = JSONResponse.extract_data(
            response=await NodeModel.set_node_availability(node_id, True)
        )
        if error:
            return update

        NodeManager.update_availability(node_id, True)
        return JSONResponse.API_1000_Success

    @ExceptionLogger.handle_program_exception_async
    async def disableNode(node_id: int):
        """禁用子节点"""
        node = NodeManager.get_node(node_id)
        
        path = f"/api/maintenance/state/"
        params = {
            "available": False
        }
        error, update = JSONResponse.extract_data(
            response=await NodeAPI.patch(node, path, params)
        )
        if error:
            return update

        error, update = JSONResponse.extract_data(
            response=await NodeModel.set_node_availability(node_id, False)
        )
        if error:
            return update

        NodeManager.update_availability(node_id, False)
        return JSONResponse.API_1000_Success
