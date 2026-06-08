from typing import Dict, List, Any
from pymysql.cursors import Cursor


def read_node_info(cursor: Cursor) -> Dict[int, List[Any]]:
    """读取子节点连接信息

    Returns:
        dict: {node_id: [region_name, host, port, token, is_available], ...}
        未配置 host/port/token 的节点不会被返回，
        is_available=0 的节点由调用方决定是否跳过
    """
    sql = """
        SELECT
            i.id,
            r.name,
            i.host,
            i.port,
            i.token,
            i.is_available
        FROM T_node_info i
        INNER JOIN D_region r
           ON r.id = i.id
        WHERE i.host IS NOT NULL
          AND i.port IS NOT NULL
          AND i.token IS NOT NULL
        ORDER BY i.id;
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        result[row[0]] = [row[1], row[2], row[3], row[4], row[5]]
    return result

def read_game_version(cursor: Cursor) -> Dict[int, str | None]:
    result = {
        1: None,
        2: None
    }
    for cid in [1,2]:
        sql = """
            SELECT game_version 
            FROM T_game_version 
            WHERE corporation_id = %s 
            AND is_latest = TRUE
            LIMIT 1;
        """
        cursor.execute(sql, [cid])
        data = cursor.fetchone()
        if data:
            result[cid] = data[0]
    return result


def update_game_version(cursor: Cursor, cid: int, local: str, latest: str) -> None:
    if latest is None or local == latest:
        return
    
    sql = """
        UPDATE T_game_version 
        SET is_latest = FALSE
        WHERE corporation_id = %s 
        AND is_latest = TRUE;
    """
    cursor.execute(sql, [cid])
    
    sql = """
        INSERT INTO T_game_version (
            corporation_id, corporation_name, is_latest, game_version
        ) VALUES (
            %s, %s, TRUE, %s
        );
    """
    name = {
        1: 'wg',
        2: 'lesta'
    }.get(cid)
    cursor.execute(sql, [cid, name, latest])

def write_node_data(cursor: Cursor, node_id: int, data: dict) -> None:
    """将单个子节点的 API 返回数据写入五张统计表

    Args:
        cursor:  数据库游标
        node_id: 子节点 ID（对应 D_region.id）
        data:    fetch_database_meta 返回的 data 字段
    """
    user_meta   = data.get("user", {})
    clan_meta   = data.get("clan", {})
    cache_meta  = data.get("cache", {})
    mysql_meta  = data.get("mysql", {})
    sqlite_meta = data.get("sqlite", {})

    # T_node_entitys — 实体数量
    cursor.execute(
        """
        UPDATE T_node_entitys
        SET users      = %s,
            clans      = %s,
            recent_lv1 = %s,
            recent_lv2 = %s
        WHERE id = %s
        """,
        (
            user_meta.get("total", 0),
            clan_meta.get("total", 0),
            user_meta.get("recent_lv1", 0),
            user_meta.get("recent_lv2", 0),
            node_id,
        ),
    )

    # T_node_cache — 缓存数据量
    cursor.execute(
        """
        UPDATE T_node_cache
        SET users    = %s,
            ships    = %s,
            battles  = %s,
            ranking  = %s
        WHERE id = %s
        """,
        (
            cache_meta.get("users", 0),
            cache_meta.get("ships", 0),
            cache_meta.get("battles", 0),
            cache_meta.get("rows", 0),
            node_id,
        ),
    )

    # T_node_db — 数据库元信息
    cursor.execute(
        """
        UPDATE T_node_db
        SET main_db_tables = %s,
            main_db_rows   = %s,
            main_db_size   = %s,
            snapshot_files = %s,
            snapshot_size  = %s
        WHERE id = %s
        """,
        (
            mysql_meta.get("tables", 0),
            mysql_meta.get("rows", 0),
            mysql_meta.get("size_kb", 0),
            sqlite_meta.get("files", 0),
            sqlite_meta.get("size_kb", 0),
            node_id,
        ),
    )

    # T_node_user_activity — 用户活跃度分布 lv_0 ~ lv_9
    user_activity = user_meta.get("activity", {})
    cursor.execute(
        """
        UPDATE T_node_user_activity
        SET lv_0 = %s,
            lv_1 = %s,
            lv_2 = %s,
            lv_3 = %s,
            lv_4 = %s,
            lv_5 = %s,
            lv_6 = %s,
            lv_7 = %s,
            lv_8 = %s,
            lv_9 = %s
        WHERE id = %s
        """,
        (
            user_activity.get("0", 0),
            user_activity.get("1", 0),
            user_activity.get("2", 0),
            user_activity.get("3", 0),
            user_activity.get("4", 0),
            user_activity.get("5", 0),
            user_activity.get("6", 0),
            user_activity.get("7", 0),
            user_activity.get("8", 0),
            user_activity.get("9", 0),
            node_id,
        ),
    )

    # T_node_clan_activity — 工会活跃度分布 lv_0 ~ lv_3
    clan_activity = clan_meta.get("activity", {})
    cursor.execute(
        """
        UPDATE T_node_clan_activity
        SET lv_0 = %s,
            lv_1 = %s,
            lv_2 = %s,
            lv_3 = %s
        WHERE id = %s
        """,
        (
            clan_activity.get("0", 0),
            clan_activity.get("1", 0),
            clan_activity.get("2", 0),
            clan_activity.get("3", 0),
            node_id,
        ),
    )