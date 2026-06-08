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

def parse_ship_row(row: dict) -> dict:
    """将 CSV 行解析为用于插入的船只参数字典"""
    ship_id = int(row['ship_id'])
    prefix, _ = row['index'].split('_', 1)  # 拆分为 index_code 的前缀和名称
    return {
        'ship_id': ship_id,
        'is_old': bool(int(row.get('is_old', 0))),
        'tier': int(row['tier']),
        'type_id': TYPE_MAP.get(row['type'], 1),
        'nation_id': NATION_MAP.get(row['nation'], 1),
        'rarity_id': RARITY_MAP.get(row.get('rarity', '')),
        'premium': bool(int(row.get('premium', 0))),
        'special': bool(int(row.get('special', 0))),
        'index_code': prefix,
        'zh_cn': row.get('zh_cn', ''),
        'zh_sg': row.get('zh_sg', ''),
        'zh_tw': row.get('zh_tw', ''),
        'en_short': row.get('en_short', ''),
        'en_full': row.get('en_full', ''),
        'ja': row.get('ja', ''),
        'ru': row.get('ru', ''),
        'verify': bool(int(row.get('verify', 0))),
    }


def main():
    """从CSV文件批量更新所有船只相关表"""
    
    for cid in [1,2]:
        file_path= {
            1: ROOT_DIR / 'init/data/ship_name_wg.csv',
            2: ROOT_DIR / 'init/data/ship_name_lesta.csv'
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
            cursor.execute(
                """SELECT game_version
                   FROM T_game_version
                   WHERE corporation_id = %s
                   AND is_latest = TRUE
                   LIMIT 1""",
                [cid]
            )
            data = cursor.fetchone()
            game_version = data[0] if data else None

            cursor.execute(
                """SELECT ship_id, is_enabled
                   FROM T_ship_info
                   WHERE corporation_id = %s""",
                [cid]
            )
            all_ship_ids = []
            local_ship_ids = []
            for row in cursor.fetchall():
                all_ship_ids.append(row[0])
                if row[1]:
                    local_ship_ids.append(row[0])

            csv_ships: dict[int, dict] = {}
            for row in raw_ships:
                ship = parse_ship_row(row)
                csv_ships[ship['ship_id']] = ship

            insert_count = 0
            update_count = 0
            dup_cleaned = 0

            for ship_id, ship in csv_ships.items():
                if ship_id not in all_ship_ids:
                    # 数据库中不存在 → INSERT
                    insert_count += 1
                    cursor.execute(
                        """INSERT INTO T_ship_info
                           (corporation_id, ship_id, is_enabled, is_old, tier,
                            type_id, nation_id, rarity_id, premium, special,
                            index_code)
                           VALUES
                           (%s, %s, TRUE, %s, %s, %s, %s, %s, %s, %s, %s);""",
                        [cid, ship['ship_id'], ship['is_old'], ship['tier'],
                         ship['type_id'], ship['nation_id'], ship['rarity_id'],
                         ship['premium'], ship['special'], ship['index_code']]
                    )
                    cursor.execute(
                        """INSERT INTO T_ship_name
                           (corporation_id, ship_id,
                            zh_cn, zh_sg, zh_tw,
                            en_short, en_full, ja, ru, verify)
                           VALUES
                           (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                        [cid, ship['ship_id'],
                         ship['zh_cn'], ship['zh_sg'], ship['zh_tw'],
                         ship['en_short'], ship['en_full'], ship['ja'],
                         ship['ru'], ship['verify']]
                    )
                    cursor.execute(
                        """INSERT INTO T_ship_nickname_zh
                           (corporation_id, ship_id)
                           VALUES (%s, %s);""",
                        [cid, ship['ship_id']]
                    )
                else:
                    # 数据库中存在 → UPDATE
                    update_count += 1

                    cursor.execute(
                        """UPDATE T_ship_info
                           SET is_enabled = TRUE,
                               is_old     = %s,
                               tier       = %s,
                               type_id    = %s,
                               nation_id  = %s,
                               rarity_id  = %s,
                               premium    = %s,
                               special    = %s,
                               index_code = %s
                           WHERE ship_id = %s;""",
                        [ship['is_old'], ship['tier'],
                         ship['type_id'], ship['nation_id'], ship['rarity_id'],
                         ship['premium'], ship['special'], ship['index_code'],
                         ship_id]
                    )
                    # 已存在 → UPDATE
                    cursor.execute(
                        """UPDATE T_ship_name
                           SET zh_cn    = %s,
                               zh_sg    = %s,
                               zh_tw    = %s,
                               en_short = %s,
                               en_full  = %s,
                               ja       = %s,
                               ru       = %s,
                               verify   = %s
                           WHERE corporation_id = %s
                           AND ship_id = %s;""",
                        [ship['zh_cn'], ship['zh_sg'], ship['zh_tw'],
                         ship['en_short'], ship['en_full'], ship['ja'],
                         ship['ru'], ship['verify'],
                         cid, ship_id]
                    )

            ships_to_disable = set(local_ship_ids) - set(csv_ships.keys())
            for ship_id in ships_to_disable:
                if local_ship_ids[ship_id]:
                    dup_cleaned += 1
                    cursor.execute(
                        """UPDATE T_ship_info
                            SET is_enabled = FALSE
                            WHERE corporation_id = %s
                            AND ship_id = %s;""",
                        [cid, ship_id]
                    )

            cursor.execute(
                """UPDATE T_ship_base
                   SET name_version = %s,
                       ship_count   = %s
                   WHERE id = %s""",
                [game_version, len(csv_ships), cid]
            )
            name = {
                1: 'wg',
                2: 'lesta'
            }.get(cid)
            logger.info(f'{name.upper()} - Insert: {insert_count},  Update: {update_count},  Delete: {dup_cleaned}')
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Rolled back")
            raise
        finally:
            cursor.close()
            conn.close()
    


if __name__ == '__main__':
    """船只数据初始化工具

    使用示例：
    python init/scripts/update_ship.py
    """
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")