import os
import csv
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

CSV_HEADERS = [
    'ship_id', 'is_old', 'tier', 'type_id', 'nation_id', 'rarity_id', 'premium', 'special',
    'index', 'default', 'zh_cn', 'zh_sg', 'zh_tw', 'en_short', 'en_full', 'ja', 'ru'
]

def main():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            for cid in [1, 2]:
                sql = """
                    SELECT 
                        i.ship_id, i.is_old, i.tier, i.type_id, i.nation_id, i.rarity_id, 
                        i.premium, i.special, i.index_code, i.ship_name, n.zh_cn, n.zh_sg, 
                        n.zh_tw, n.en_short, n.en_full, n.ja, n.ru 
                    FROM T_ship_info i 
                    INNER JOIN T_ship_name n 
                    ON i.corporation_id = n.corporation_id 
                    AND i.ship_id = n.ship_id 
                    WHERE i.corporation_id = %s 
                    AND i.is_enabled = 1 
                    AND i.is_demo = 0
                    ORDER BY i.id;
                """
                cursor.execute(sql, [cid])
                rows = cursor.fetchall()
                corporation = {
                    1: 'wg',
                    2: 'lesta'
                }.get(cid)
                csv_path = ROOT_DIR / f'temp/ship_name_{corporation}.csv'
                if csv_path.exists():
                    csv_path.unlink()
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(CSV_HEADERS)
                    for row in rows:
                        writer.writerow(row)

                logger.info(f'Exported: {csv_path}')
    finally:
        conn.close()


if __name__ == '__main__':
    """执行 sql 语句
    
    使用示例：
    python scripts/tools/export_ship.py
    """

    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")