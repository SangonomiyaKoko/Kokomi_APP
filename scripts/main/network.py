import requests
import traceback

from logger import logger
from exception import write_exception
from settings import TEMP_DIR


def fetch_data(url: str, header: dict):
    """发送 GET 请求并解析 JSON 响应"""
    resp = requests.get(url, headers=header, timeout=5)

    if resp.status_code == 200:
        return resp.json()
    resp.raise_for_status()

def fetch_binary_file(base_url: str, token: str, index: str, region: str):
    """
    从 GET 接口下载二进制文件并保存到本地
    先写入临时 .filepart 文件，完成后重命名（覆盖已有文件）
    
    Args:
        base_url: 基础 URL
        token: 认证 token
        index: 文件类型索引（如 'clan', 'user'）
        region_id: 区域 ID
    """
    chunk_size = 8192
    headers = {'Access-Token': token}
    
    url = f'{base_url}/api/maintenance/ranking/download/?file_type={index}_ranking'
    # 最终目标路径
    output_path = TEMP_DIR / f'{index}_ranking_{region}.msgpack'
    # 临时文件路径
    part_path = TEMP_DIR / f'{index}_ranking_{region}.msgpack.filepart'
    
    try:
        # 确保目录存在
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        with requests.get(url, headers=headers, stream=True, timeout=5) as resp:
            resp.raise_for_status()

            # 写入临时文件
            with open(part_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            # 下载完成，重命名临时文件为目标文件（覆盖已存在的目标）
            part_path.replace(output_path)
            logger.info(f'Successfully downloaded: {output_path}')
            
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"Download file failed: {error_name}")
        write_exception(
            error_type="NetworkError",
            error_name=error_name,
            error_info=traceback.format_exc()
        )
        # 清理可能残留的临时文件
        if part_path.exists():
            part_path.unlink()

def fetch_database_meta(base_url: str, token: str):
    """获取节点数据库数据"""
    try:
        headers = {
            'Access-Token': token
        }
        # http://127.0.0.1:8000/api/maintenance/database/meta/
        url = f'{base_url}/api/maintenance/database/meta/'
        return fetch_data(url, headers)
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"Fetch database meta failed: {error_name}")
        write_exception(
            error_type="NetworkError",
            error_name=error_name,
            error_info=traceback.format_exc()
        )
        return

def download_ranking_file(base_url: str, token: str):
    """获取节点数据库数据"""
    try:
        header = {
            'Access-Token': token
        }
        # http://127.0.0.1:8000/api/maintenance/ranking/download/?file_type=ship_ranking
        url = f'{base_url}/api/maintenance/ranking/download/?file_type=ship_ranking'
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