import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime


CLIENT_NAME = 'Maintenance'
REFRESH_INTERVAL = 600
DATE_FMT = '%Y-%m-%d %H:%M:%S'
USE_TQDM = sys.stdout.isatty() # 只有在交互式终端中才使用tqdm显示进度条

ROOT_DIR = Path(os.getcwd())
LOG_DIR = ROOT_DIR / 'logs'


# 关闭代理，避免请求外部API时被本地环境变量干扰
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

if not load_dotenv('.env'):
    # 开发环境下如果加载env.dev失败，直接退出程序
    print(f"{datetime.now().strftime(DATE_FMT)} [ERROR] Failed to load .env configuration")
    exit(1)
print(f"{datetime.now().strftime(DATE_FMT)} [INIT] Env config loaded: .env")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "autocommit": False  # 关闭自动提交，改为手动控制事务，以便在发生异常时能正确回滚，保证数据一致性
}

print(f"{datetime.now().strftime(DATE_FMT)} [INIT] Configuration data loading complete")