from api.loggers import ExceptionLogger

from .node import NodeManager, NodeInfo


class NodeAPI:
    @ExceptionLogger.handle_network_exception_async
    async def get(
        node: NodeInfo, 
        path: str = '/', 
        params: dict = {}
    ):
        headers = {
            'access-token': node.token
        }
        node_url = f'http://{node.host}:{node.port}'
        url = node_url + path

        client = NodeManager.get_client()

        resp = await client.get(
            url=url, 
            params=params, 
            headers=headers
        )
        if resp.status_code == 200:
            return resp.json()
        
        resp.raise_for_status()
        
    @ExceptionLogger.handle_network_exception_async
    async def patch(
        node: NodeInfo, 
        path: str = '/', 
        params: dict = {}
    ):
        headers = {
            'access-token': node.token
        }
        node_url = f'http://{node.host}:{node.port}'
        url = node_url + path

        client = NodeManager.get_client()

        resp = await client.patch(
            url=url, 
            params=params, 
            headers=headers
        )
        if resp.status_code == 200:
            return resp.json()
        
        resp.raise_for_status()