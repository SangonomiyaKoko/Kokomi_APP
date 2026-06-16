from api.response import JSONResponse
from api.loggers import ExceptionLogger
from api.network import NodeAPI, NodeManager
from api.models import AccountModel


class UserRefreshAPI:
    @ExceptionLogger.handle_program_exception_async
    async def refresh_user(
        region_id: int, 
        account_id: int
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = f"/api/platform/user/{account_id}/"
        params = {}
        response = await NodeAPI.patch(node, path, params)

        error, user_basic = JSONResponse.extract_data(
            response=response
        )
        if error:
            return user_basic
        
        error, refresh = JSONResponse.extract_data(
            response=await AccountModel.refresh_account_base(
                region_id=region_id, 
                account_id=account_id, 
                user_name=user_basic.get('basic', {}).get('username', f'User_{account_id}'),
                created_at=user_basic.get('basic', {}).get('created_at')
            )
        )
        if error:
            return refresh

        return response