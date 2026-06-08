#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gc
import time
import pymysql
import traceback
from pymysql import Connection

from logger import logger
from exception import write_exception
from network import fetch_database_meta
from db_ops import (
    read_node_info,
    read_game_version, 
    update_game_version,
    write_node_data
)
from settings import (
    CLIENT_NAME,
    REFRESH_INTERVAL,
    MYSQL_CONFIG
)


def worker(mysql_connection: Connection) -> None:
    """单轮缓存更新执行体

    从主数据库读取子节点信息，逐个获取各子节点的数据库元数据并写入表中

    Args:
        mysql_connection: MySQL 数据库连接
    """
    try:
        with mysql_connection.cursor() as cursor:
            node_info = read_node_info(cursor)
            game_version = read_game_version(cursor)
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"Failed to read node info: {error_name}")
        write_exception(
            error_type="DatabaseError",
            error_name=error_name,
            error_info=traceback.format_exc(),
        )
        return
    
    total_users = 0
    total_clans = 0

    for node_id, node_data in node_info.items():
        name, host, port, token, is_available = node_data

        if not is_available:
            logger.info(f"Node {name.upper()} is marked unavailable")
            continue

        base_url = f"http://{host}:{port}"

        response = fetch_database_meta(base_url, token)

        if response is None or response.get("code") != 1000:
            logger.error(f"Node {name} exception: {response}")
            continue

        data = response.get("data", {})
        version = data.get('version')
        user_meta = data.get("user", {})
        clan_meta = data.get("clan", {})
        cache_meta = data.get("cache", {})
        total_users += user_meta.get('total', 0)
        total_clans += clan_meta.get('total', 0)
        logger.info(
            f"Node {name.upper().ljust(4)} — "
            f"users: {str(user_meta.get('total', 0)).rjust(7)},  "
            f"clans: {str(clan_meta.get('total', 0)).rjust(6)},  "
            f"cached: {str(cache_meta.get('users', 0)).rjust(7)},  " 
            f"version: {version}"
        )

        try:
            with mysql_connection.cursor() as cursor:
                write_node_data(cursor, node_id, data)
                if node_id == 3:
                    update_game_version(cursor, 1, game_version.get(1), version)
                elif node_id == 4:
                    update_game_version(cursor, 2, game_version.get(2), version)

            mysql_connection.commit()
        except Exception as e:
            mysql_connection.rollback()
            error_name = type(e).__name__
            logger.error(f"Database operation exception: {error_name}")
            write_exception(
                error_type="DatabaseError",
                error_name=error_name,
                error_info=traceback.format_exc(),
            )
    
    logger.info(
        f"Summary   — "
        f"users: {total_users},  "
        f"clans: {total_clans}"
    )


def main():
    """主调度循环

    无限循环执行：建立连接 → worker() 更新缓存 → 释放连接资源 →
    按 REFRESH_INTERVAL 补齐 sleep。
    异常不会中断循环，但会清理服务状态 key 以便外部监控感知。
    """
    mysql_connection = None

    while True:
        start = time.monotonic()

        try:
            mysql_connection = pymysql.connect(**MYSQL_CONFIG)

            worker(
                mysql_connection=mysql_connection
            )
        except Exception as e:
            error_name = type(e).__name__
            logger.error(f"A fatal error occurred in the loop: {error_name}")
            write_exception(
                error_type="ProgramError",
                error_name=error_name,
                error_info=traceback.format_exc(),
            )
        finally:
            if mysql_connection:
                mysql_connection.close()
            mysql_connection = None

            gc.collect()

        # 计算本次循环的实际运行时间，并根据刷新间隔决定是否需要 sleep
        elapsed = time.monotonic() - start
        logger.info("This loop took %.2f seconds", round(elapsed, 2))
        sleep_time = max(0, round(REFRESH_INTERVAL - elapsed, 2))

        if sleep_time >= 1:
            logger.info(f"The process sleeps for {sleep_time} seconds")
            time.sleep(sleep_time)
        else:
            logger.info("The process sleeps for 1 seconds")
            time.sleep(1)
        logger.info("-" * 70)


def handler(*_):
    """信号处理器，退出"""
    logger.info("The process is closing")
    os._exit(0)


if __name__ == "__main__":
    logger.info("Start running service: %s", CLIENT_NAME)
    logger.info("Service refresh interval: %s seconds", REFRESH_INTERVAL)

    if os.name != "nt":
        # 在非 Windows 系统上注册 SIGTERM 信号处理器
        import signal

        signal.signal(signal.SIGTERM, handler)

    try:
        main()
    except KeyboardInterrupt:
        # 在 Windows 系统上通过 KeyboardInterrupt 实现类似的退出功能
        handler()
