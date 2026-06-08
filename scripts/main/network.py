import requests
import traceback

from logger import logger
from exception import write_exception


def fetch_data(url: str, header: dict):
    """发送 GET 请求并解析 JSON 响应"""
    resp = requests.get(url, headers=header, timeout=5)

    if resp.status_code == 200:
        return resp.json()
    resp.raise_for_status()

def fetch_database_meta(base_url: str, token: str):
    """获取节点数据库数据"""
    try:
        header = {
            'Access-Token': token
        }
        # http://127.0.0.1:8000/api/maintenance/database/meta/
        url = f'{base_url}/api/maintenance/database/meta/'
        return fetch_data(url, header)
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"Fetch database meta failed: {error_name}")
        write_exception(
            error_type="NetworkError",
            error_name=error_name,
            error_info=traceback.format_exc()
        )
        return
    
"""
正常返回值
{
  "status": "ok",
  "code": 1000,
  "message": "Success",
  "data": {
    "user": {
      "total": 45,
      "recent_lv1": 1,
      "recent_lv2": 1,
      "activity": {
        "0": 6,
        "1": 15,
        "2": 5,
        "3": 6,
        "4": 10,
        "5": 3,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0
      }
    },
    "clan": {
      "total": 1,
      "activity": {
        "0": 0,
        "1": 1,
        "2": 0,
        "3": 0
      }
    },
    "cache": {
      "users": 39,
      "ships": 11097,
      "battles": 341921,
      "rows": 0
    },
    "mysql": {
      "tables": 40,
      "rows": 13500,
      "size_kb": 6112
    },
    "sqlite": {
      "files": 2,
      "size_kb": 316
    }
  }
}
"""