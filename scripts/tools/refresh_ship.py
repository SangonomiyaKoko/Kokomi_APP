
import os
import logging
import pymysql
import requests
import argparse
from pathlib import Path
from dotenv import load_dotenv
from pymysql.cursors import Cursor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(os.getcwd())

# 加载环境变量
if (ROOT_DIR / '.env').exists():
    logger.info('Loading environment file: .env')
    load_dotenv('.env')
else:
    raise FileNotFoundError('No environment file found')

DB_CONFIG = {
    "host": 'localhost',
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": 'root',
    "password": os.getenv("MYSQL_ROOT_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    'autocommit': False
}

# 类型映射（来自 D_ship_type）
TYPE_MAP = {
    'AirCarrier': 1,
    'Battleship': 2,
    'Cruiser': 3,
    'Destroyer': 4,
    'Submarine': 5
}

# 国家映射（来自 D_ship_nation）
NATION_MAP = {
    'usa': 1,
    'japan': 2,
    'germany': 3,
    'uk': 4,
    'ussr': 5,
    'france': 6,
    'italy': 7,
    'pan_asia': 8,
    'europe': 9,
    'netherlands': 10,
    'commonwealth': 11,
    'pan_america': 12,
    'spain': 13
}

# 稀有度映射（来自 D_ship_rarity）
RARITY_MAP = {
    '': None,
    'Common': 1,
    'Uncommon': 2,
    'Rare': 3,
    'Epic': 4,
    'Legendary': 5
}

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
        logger.info(f'GET {url}')
        response = fetch_data(url)

        if type(response) == str:
            logger.warning(f"Fetch ship data failed: {response}")
            return

        return response
    except Exception as e:
        error_name = type(e).__name__
        logger.warning(f"Fetch ship data failed: {error_name}")

def read_ship_info(cursor: Cursor, cid: int):
    sql = """
        SELECT 
            ship_id, 
            is_enabled 
        FROM T_ship_info 
        WHERE corporation_id = %s 
        ORDER BY id;
    """
    cursor.execute(sql, [cid])
    data = cursor.fetchall()

    existing_ship_ids = []
    enabled_ship_ids = []
    for ship in data:
        existing_ship_ids.append(ship[0])
        if ship[1]:
            enabled_ship_ids.append(ship[0])
    return [existing_ship_ids, enabled_ship_ids]

def read_game_version(cursor: Cursor, cid: int):
    sql = """
        SELECT game_version 
        FROM T_game_version 
        WHERE is_latest = 1 
          AND corporation_id = %s;
    """
    cursor.execute(sql, [cid])
    data = cursor.fetchone()
    return data[0]

def refresh_ship_name(cursor: Cursor, cid: int, response: dict, ship_info: list, version: str):
    latest_data = {}
    existing_ship_ids, enabled_ship_ids = ship_info

    # 解析数据
    for ship_id, ship_data in response.items():
        ship_tags = ship_data.get('tags', [])

        # 去除测试船只
        if 'demoWithoutStats' in ship_tags or 'demoWithoutStatsPrem' in ship_tags:
            is_demo = True
        else:
            is_demo = False

        loc = ship_data.get('localization', {})
        if cid == 1:
            default_name: str = loc.get('shortmark', {})['en']
        else:
            default_name: str = loc.get('shortmark', {})['ru']

        if default_name.startswith('[') and default_name.endswith(']'):
            continue

        prefix, name = ship_data['name'].split('_', 1) 

        latest_data[int(ship_id)] = {
            'is_demo': is_demo,
            'tier': ship_data['level'],
            'type_id': TYPE_MAP.get(ship_tags[0], 1),
            'nation_id': NATION_MAP.get(ship_data['nation'], 1),
            'premium': 1 if "uiPremium" in ship_tags else 0,
            'special': 1 if "uiSpecial" in ship_tags else 0,
            'index': prefix,
            'name': name,
            'en_short': default_name,
            'en_full': loc.get('mark', {}).get('en', default_name),
            'zh_cn': loc.get('shortmark', {}).get('zh_cn'),
            'zh_sg': loc.get('shortmark', {}).get('zh_sg', default_name),
            'zh_tw': loc.get('shortmark', {}).get('zh_tw'),
            'ja': loc.get('shortmark', {}).get('ja', default_name),
            'ru': loc.get('shortmark', {}).get('ru', default_name)
        }

    changed_rows = [0] * 3
    for ship_id, ship in latest_data.items():
        if ship_id not in existing_ship_ids:
            cursor.execute(
                """INSERT INTO T_ship_info
                    (corporation_id, ship_id, is_enabled, is_old, is_demo, tier,
                    type_id, nation_id, rarity_id, premium, special,
                    index_code, ship_name)
                    VALUES
                    (%s, %s, TRUE, FALSE, %s, %s, %s, %s, NULL, %s, %s, %s, %s);""",
                [cid, ship_id, ship['is_demo'], ship['tier'], ship['type_id'], ship['nation_id'],
                    ship['premium'], ship['special'], ship['index'], ship['name']]
            )
            cursor.execute(
                """INSERT INTO T_ship_name
                    (corporation_id, ship_id,
                    zh_cn, zh_sg, zh_tw,
                    en_short, en_full, ja, ru)
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                [cid, ship_id, ship['zh_cn'], ship['zh_sg'], ship['zh_tw'],
                    ship['en_short'], ship['en_full'], ship['ja'], ship['ru']]
            )
            cursor.execute(
                """INSERT INTO T_ship_nickname_zh
                    (corporation_id, ship_id)
                    VALUES (%s, %s);""",
                [cid, ship_id]
            )
            changed_rows[0] += 1
            logger.info(f"C_{cid} - Insert ship: {ship_id} {ship['index']} {ship['name']}")
        else:
            cursor.execute(
                """UPDATE T_ship_info 
                SET is_demo = %s, premium = %s, special = %s, index_code = %s, ship_name = %s
                WHERE corporation_id = %s 
                  AND ship_id = %s;""",
                [ship['is_demo'], ship['premium'], ship['special'], ship['index'], ship['name'], cid, ship_id]
            )
            changed_rows[1] += 1

    for ship_id in enabled_ship_ids:
        if ship_id not in latest_data:
            cursor.execute(
                """UPDATE T_ship_info 
                SET is_enabled = FALSE 
                WHERE corporation_id = %s 
                  AND ship_id = %s;""",
                [cid, ship_id]
            )
            changed_rows[2] += 1
            logger.info(f"C_{cid} - Disable ship: {ship_id}")

    cursor.execute(
        """UPDATE T_ship_base 
        SET name_version = %s, ship_count = %s, updated_at = NOW() 
        WHERE id = %s;""",
        [version, len(latest_data), cid]
    )
    logger.info(f'Updated: {changed_rows}')

def main(cid: int):
    if cid not in [1,2]:
        logger.warning(F"Invaild args: {cid}")
        return 
    
    api_response = fetch_ship_data(cid)

    if api_response:
        conn = pymysql.connect(**DB_CONFIG)
        try:
            with conn.cursor() as cursor:
                ship_info = read_ship_info(cursor, cid)
                version = read_game_version(cursor, cid)
                refresh_ship_name(cursor, cid, api_response, ship_info, version)
            conn.commit()
        except Exception:
            logger.exception("Execute failed, rolled back")
            conn.rollback()
        finally:
            conn.close()
    else:
        logger.warning('Load data failed')

if __name__ == '__main__':
    """执行 sql 语句
    
    使用示例：
    python scripts/tools/refresh_ship.py -c 1
    python scripts/tools/refresh_ship.py -c 2
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--cid', 
        required=True, 
        type=int, 
        help='CID'
    )
    args = parser.parse_args()
    cid = args.cid
    try:
        main(cid)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")