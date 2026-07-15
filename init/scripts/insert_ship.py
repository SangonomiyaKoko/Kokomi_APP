import os
import csv
import json
import logging
import pymysql
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(os.getcwd())

if (ROOT_DIR / '.env').exists():
    logger.info('Loading environment file: .env')
    load_dotenv('.env')
else:
    raise FileNotFoundError('No environment file found')

DB_CONFIG = {
    "host": 'localhost',
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    'autocommit': False
}

def parse_ship_row(row: dict) -> dict:
    """将 CSV 行解析为用于插入的船只参数字典"""
    ship_id = int(row['ship_id'])
    return {
        'ship_id': ship_id,
        'is_old': bool(int(row.get('is_old', 0))),
        'tier': int(row['tier']),
        'type_id': int(row['type_id']),
        'nation_id': int(row['nation_id']),
        'rarity_id': row.get('rarity_id'),
        'premium': bool(int(row.get('premium', 0))),
        'special': bool(int(row.get('special', 0))),
        'index': row.get('index'),
        'name': row.get('default'),
        'zh_cn': row.get('zh_cn'),
        'zh_sg': row.get('zh_sg'),
        'zh_tw': row.get('zh_tw'),
        'en_short': row.get('en_short'),
        'en_full': row.get('en_full'),
        'ja': row.get('ja'),
        'ru': row.get('ru')
    }


def main():
    """从CSV文件批量更新所有船只相关表"""
    
    for cid in [1,2]:
        file_path= {
            1: ROOT_DIR / 'temp/ship_name_wg.csv',
            2: ROOT_DIR / 'temp/ship_name_lesta.csv'
        }.get(cid)

        if not file_path.exists():
            logger.error(f"CSV file not found: {file_path}")
            continue
        

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                raw_ships = list(reader)
            logger.info(f'Found {len(raw_ships)} ships in CSV')
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            continue

        latest_ship_ids = [int(row['ship_id']) for row in raw_ships]
        if len(latest_ship_ids) <= 0:
            continue

        conn = pymysql.connect(**DB_CONFIG)
        try:
            cursor = conn.cursor()

            # 查询当前游戏版本
            cursor.execute("""
                SELECT game_version
                FROM T_game_version
                WHERE corporation_id = %s
                AND is_latest = TRUE
                LIMIT 1
                """, [cid])
            data = cursor.fetchone()
            game_version = data[0] if data else None

            csv_ships = [parse_ship_row(row) for row in raw_ships]

            for ship in csv_ships:
                cursor.execute(
                    """INSERT INTO T_ship_info
                        (corporation_id, ship_id, is_enabled, is_old, is_demo, tier,
                        type_id, nation_id, rarity_id, premium, special,
                        index_code, ship_name)
                        VALUES
                        (%s, %s, TRUE, %s, FALSE, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    [cid, ship['ship_id'], ship['is_old'], ship['tier'],
                        ship['type_id'], ship['nation_id'], ship['rarity_id'] if ship['rarity_id'] != '' else None,
                        ship['premium'], ship['special'], ship['index'], ship['name']]
                )
                cursor.execute(
                    """INSERT INTO T_ship_name
                        (corporation_id, ship_id,
                        zh_cn, zh_sg, zh_tw,
                        en_short, en_full, ja, ru)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    [cid, ship['ship_id'],
                        ship['zh_cn'], ship['zh_sg'], ship['zh_tw'],
                        ship['en_short'], ship['en_full'], ship['ja'],
                        ship['ru']]
                )
                cursor.execute(
                    """INSERT INTO T_ship_nickname_zh
                        (corporation_id, ship_id)
                        VALUES (%s, %s);""",
                    [cid, ship['ship_id']]
                )
                
            if game_version:
                cursor.execute(
                    """UPDATE T_ship_base
                    SET name_version = %s,
                        ship_count   = %s
                    WHERE id = %s""",
                    [game_version, len(csv_ships), cid]
                )
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Rolled back")
            raise
        finally:
            conn.close()
    


if __name__ == '__main__':
    """船只数据初始化工具

    使用示例：
    python init/scripts/insert_ship.py
    """
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")