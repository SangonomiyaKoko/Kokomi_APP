#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gc
import time
import redis
import pymysql
import traceback
from redis import Redis
from pymysql import Connection

from logger import logger
from exception import write_exception
from game_api import fetch_ship_data
from network import fetch_node_status, fetch_database_meta, fetch_binary_file, post_ship_data
from ranking import clan_ranking, user_ranking
from db_ops import (
    read_node_info,
    read_name_version,
    read_game_version, 
    read_ship_info,
    read_ship_hash,
    update_game_version,
    refresh_ship_name,
    write_node_data
)
from utils import generate_ship_hash
from settings import (
    CLIENT_NAME,
    REFRESH_INTERVAL,
    MYSQL_CONFIG,
    REDIS_CONFIG,
    REDIS_PROTOCOL
)


def worker(mysql_connection: Connection, redis_client: Redis) -> None:
    """单轮缓存更新执行体

    从主数据库读取子节点信息，逐个获取各子节点的数据库元数据并写入表中

    Args:
        mysql_connection: MySQL 数据库连接
    """
    try:
        with mysql_connection.cursor() as cursor:
            node_info = read_node_info(cursor)
            game_version = read_game_version(cursor)
            name_version = read_name_version(cursor)
            ship_info = read_ship_info(cursor)
            ship_hash = read_ship_hash(cursor)
    except Exception as e:
        error_name = type(e).__name__
        logger.error(f"Failed to read node info: {error_name}")
        write_exception(
            error_type="DatabaseError",
            error_name=error_name,
            error_info=traceback.format_exc(),
        )
        return
    
    logger.info(f'Local version: {game_version}')
    wg_ship_hash = generate_ship_hash(ship_hash[1])
    logger.info(f'Ship name 1: {name_version[1]} - {len(ship_info[1][1])} - ({len(ship_hash[1])}){wg_ship_hash}')
    lesta_ship_hash = generate_ship_hash(ship_hash[2])
    logger.info(f'Ship name 2: {name_version[2]} - {len(ship_info[2][1])} - ({len(ship_hash[2])}){lesta_ship_hash}')
    
    total_users = 0
    total_clans = 0
    total_error = 0
    latest_version = {1: None, 2: None}

    for node_id, node_data in node_info.items():
        name, host, port, token, is_available = node_data

        if not is_available:
            logger.info(f"Node {name.upper()} is marked unavailable")
            continue

        base_url = f"http://{host}:{port}"

        response = fetch_node_status(base_url, token)

        if response is None or response.get("code") != 1000:
            logger.error(f"Node {name} exception: {response}")
            continue

        data = response.get("data", {})
        available = data.get('available', False)
        name_hash = data.get('name_hash')

        response = fetch_database_meta(base_url, token)

        if response is None or response.get("code") != 1000:
            logger.error(f"Node {name} exception: {response}")
            continue

        data = response.get("data", {})
        error = data.get('error', 0)
        version = data.get('version')
        user_meta = data.get("user", {})
        clan_meta = data.get("clan", {})
        total_users += user_meta.get('total', 0)
        total_clans += clan_meta.get('total', 0)
        total_error += error
        logger.info(
            f"Node {name.upper().ljust(4)} — "
            f"State: {available},  "
            f"users: {str(user_meta.get('total', 0)).rjust(7)},  "
            f"clans: {str(clan_meta.get('total', 0)).rjust(6)},  "
            f"version: {version},  "
            f"error: {error}"
        )

        # 记录最新 Version 字段
        if node_id == 3:
            latest_version[1] = version
        elif node_id == 4:
            latest_version[2] = version

        try:
            with mysql_connection.cursor() as cursor:
                write_node_data(cursor, node_id, data)
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

        # 下载排行榜文件
        if available:
            for index in ['clan', 'ship']:
                fetch_binary_file(base_url, token, index, name)

        # 更新子服务器的船只名称字段
        if node_id == 4:
            if name_hash and lesta_ship_hash and name_hash != lesta_ship_hash:
                logger.info(f'Node {name.upper().ljust(4)} — {name_hash} -> {lesta_ship_hash}')
                result = post_ship_data(base_url, token, ship_hash[2])
                logger.info(f'Response: {result}')
        else:
            if name_hash and wg_ship_hash and name_hash != wg_ship_hash:
                logger.info(f'Node {name.upper().ljust(4)} — {name_hash} -> {wg_ship_hash}')
                result = post_ship_data(base_url, token, ship_hash[1])
                logger.info(f'Response: {result}')

    logger.info(
        f"Summary   — /             "
        f"users: {total_users},  "
        f"clans: {total_clans},  "
        "/               "
        f"error: {total_error}"
    )


    try:
        with mysql_connection.cursor() as cursor:
            # 更新 WG 运营服务器的船只信息
            if (
                name_version.get(1) is None or 
                latest_version.get(1) is None or 
                str(name_version[1]) != str(latest_version[1])
            ):
                update_game_version(cursor, 1, game_version.get(1), latest_version[1])
                logger.info(f"WG Ship Version: {name_version[1]} -> {latest_version[1]}")
                wg_response = fetch_ship_data(1)
                if wg_response:
                    refresh_ship_name(cursor, 1, wg_response, ship_info[1], latest_version[1])

            # 更新 Lesta 运营服务器的船只信息
            if (
                name_version.get(2) is None or 
                latest_version.get(2) is None or 
                str(name_version[2]) != str(latest_version[2])
            ):
                update_game_version(cursor, 2, game_version.get(2), latest_version[2])
                logger.info(f"Lesta Ship Version: {name_version[2]} -> {latest_version[2]}")
                lesta_response = fetch_ship_data(2)
                if lesta_response:
                    refresh_ship_name(cursor, 2, lesta_response, ship_info[2], latest_version[2])

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

    clan_ranking(redis_client)
    user_ranking(redis_client)

def main():
    """主调度循环

    无限循环执行：建立连接 → worker() 更新缓存 → 释放连接资源 →
    按 REFRESH_INTERVAL 补齐 sleep。
    异常不会中断循环，但会清理服务状态 key 以便外部监控感知。
    """
    redis_client = None
    mysql_connection = None

    while True:
        start = time.monotonic()

        try:
            if REDIS_PROTOCOL == '0':
                redis_client = redis.Redis(**REDIS_CONFIG)
            else:
                redis_client = redis.Redis(**REDIS_CONFIG, protocol=2)
            mysql_connection = pymysql.connect(**MYSQL_CONFIG)

            worker(
                mysql_connection=mysql_connection,
                redis_client=redis_client
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
            if redis_client:
                redis_client.close()
            if mysql_connection:
                mysql_connection.close()
            redis_client = None
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
