import requests

from logger import logger


def fetch_data(url: str):
    """发送 GET 请求并解析 JSON 响应

    Args:
        url: 请求地址

    Returns:
        成功时返回解析后的 dict，失败时返回错误标识字符串
    """
    try:
        resp = requests.get(url, timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'ok':
                return data.get('data', {})
            else:
                return "Game_API_Error"
        
        return f'HTTP_STATUS_{resp.status_code}'
    except Exception as e:
        return f'ERROR_{type(e).__name__}'

def fetch_ship_data(cid: int):
    """获取"""
    try:
        if cid == 1:
            url = 'https://vortex.worldofwarships.asia/api/encyclopedia/en/vehicles/'
        else:
            url = 'https://vortex.korabli.su/api/encyclopedia/en/vehicles/'

        response = fetch_data(url)

        if type(response) == str:
            logger.error(f"Fetch ship data failed: {response}")
            return

        return response
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"Fetch ship data failed: {error_name}")