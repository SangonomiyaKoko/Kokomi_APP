from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.models import NodeModel
from api.network import NodeManager


class NodeAPI:
    @ExceptionLogger.handle_program_exception_async
    async def enableNode(node_id: int):
        """启用子节点（写 DB → 同步内存状态）"""
        response = await NodeModel.set_node_availability(node_id, True)
        error, _ = JSONResponse.extract_data(response)
        if error:
            return response

        NodeManager.update_availability(node_id, True)
        return JSONResponse.API_1000_Success

    @ExceptionLogger.handle_program_exception_async
    async def disableNode(node_id: int):
        """禁用于节点（写 DB → 同步内存状态）"""
        response = await NodeModel.set_node_availability(node_id, False)
        error, _ = JSONResponse.extract_data(response)
        if error:
            return response

        NodeManager.update_availability(node_id, False)
        return JSONResponse.API_1000_Success
