import os
import logging
import pymysql
from pymysql.constants import CLIENT
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
    'autocommit': False
}
DATABASE = os.getenv("MYSQL_DATABASE")

def main():
    confirm = input(f"Are you sure you want to rebuild database '{DATABASE}'? (Y/N): ").strip().upper()
    if confirm != 'Y':
        logger.info("Operation cancelled by user")
        return
    
    conn = pymysql.connect(
        **DB_CONFIG,
        client_flag=CLIENT.MULTI_STATEMENTS
    )
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS `{DATABASE}`;")
    cursor.execute(f"CREATE DATABASE `{DATABASE}`;")
    cursor.execute(f"USE `{DATABASE}`;")
    sql_files = [
        ROOT_DIR / "init/mysql/01-base.sql",
        ROOT_DIR / "init/mysql/02-user.sql",
        ROOT_DIR / "init/mysql/03-ship.sql",
        ROOT_DIR / "init/mysql/04-node.sql",
        ROOT_DIR / "init/mysql/05-api.sql",
        ROOT_DIR / "init/mysql/06-app.sql",
        ROOT_DIR / "init/mysql/99-test.sql"
    ]
    for sql_file in sql_files:
        if sql_file.exists():
            with sql_file.open("r", encoding="utf-8") as f:
                sql = f.read()
                cursor.execute(sql)
        logger.info(f'Executed: {sql_file}')
    conn.commit()
    conn.close()
    logger.info(f'Success: {DATABASE}')

if __name__ == '__main__':
    """用于在数据库初始化，删除并重建数据库

    使用示例：
    python init/scripts/rebuild_db.py
    """
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")