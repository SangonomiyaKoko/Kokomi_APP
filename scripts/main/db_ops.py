from typing import Dict, List, Any
from pymysql.cursors import Cursor


from logger import logger

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

def read_name_version(cursor: Cursor) -> Dict[int, str | None]:
    sql = """
        SELECT id, name_version 
        FROM T_ship_base;
    """
    cursor.execute(sql)
    data = cursor.fetchall()

    result = {}
    for name in data:
        result[name[0]] = name[1]
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

def read_ship_hash(cursor: Cursor) -> Dict[int, str | None]:
    result = {
        1: None,
        2: None
    }
    for cid in [1,2]:
        sql = """
            SELECT 
                ship_id,
                is_old, 
                tier,
                type_id,
                nation_id,
                rarity_id, 
                premium,
                special,
                index_code,
                ship_name
            FROM T_ship_info 
            WHERE corporation_id = %s 
              AND is_enabled = 1 
              AND is_demo = 0
            ORDER BY ship_id ASC;
        """
        cursor.execute(sql, [cid])
        rows = cursor.fetchall()
            
        hash_data = {}
        for row in rows:
            ship_id = int(row[0])
            is_old = 1 if row[1] else 0
            tier = row[2]
            type_id = row[3]
            nation_id = row[4]
            rarity_id = row[5]
            premium = 1 if row[6] else 0
            special = 1 if row[7] else 0
            prefix = row[8]  # index_code
            name = row[9]
            
            hash_data[ship_id] = [
                is_old, tier, type_id, nation_id, rarity_id, 
                premium, special, prefix, name
            ]
        result[cid] = hash_data

    return result

def read_ship_info(cursor: Cursor) -> Dict[int, str | None]:
    result = {
        1: None,
        2: None
    }
    for cid in [1,2]:
        sql = """
            SELECT ship_id, is_enabled 
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

        result[cid] = [existing_ship_ids, enabled_ship_ids]

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
            logger.info(f"C_{cid} - Insert ship: {ship_id} {ship['index']} {ship['name']}")
        else:
            cursor.execute(
                """UPDATE T_ship_info 
                SET is_demo = %s, premium = %s, special = %s, index_code = %s, ship_name = %s
                WHERE corporation_id = %s 
                  AND ship_id = %s;""",
                [ship['is_demo'], ship['premium'], ship['special'], ship['index'], ship['name'], cid, ship_id]
            )

    for ship_id in enabled_ship_ids:
        if ship_id not in latest_data:
            cursor.execute(
                """UPDATE T_ship_info 
                SET is_enabled = FALSE 
                WHERE corporation_id = %s 
                  AND ship_id = %s;""",
                [cid, ship_id]
            )
            logger.info(f"C_{cid} - Disable ship: {ship_id}")
    cursor.execute(
        """UPDATE T_ship_base 
        SET name_version = %s, ship_count = %s 
        WHERE id = %s;""",
        [version, len(latest_data), cid]
    )

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