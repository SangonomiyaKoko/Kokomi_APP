-- 定义子节点信息
CREATE TABLE IF NOT EXISTS T_node_info (
    id               TINYINT      PRIMARY KEY,   -- D_region.id

    host             VARCHAR(15)  DEFAULT NULL,
    port             INT          DEFAULT NULL,
    token            VARCHAR(15)  DEFAULT NULL,
    is_available     TINYINT(1)   DEFAULT 0,  -- 0=不可用 1=可用

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_node_info 
    (id) 
VALUES
    (1), (2), (3), (4), (5);

-- 子节点实体数量信息
CREATE TABLE IF NOT EXISTS T_node_entitys (
    id               TINYINT      PRIMARY KEY,   -- D_region.id

    users            INT          DEFAULT 0,     -- 玩家id数量
    clans            INT          DEFAULT 0,     -- 工会id数量
    recent_lv1       INT          DEFAULT 0,     -- 记录近期数据功能的用户数量
    recent_lv2       INT          DEFAULT 0,     -- 记录近期数据功能（Plus）的用户数量

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_node_entitys 
    (id) 
VALUES
    (1), (2), (3), (4), (5);

-- 子节点缓存数据信息
CREATE TABLE IF NOT EXISTS T_node_cache (
    id               TINYINT      PRIMARY KEY,   -- D_region.id

    users            INT          DEFAULT 0,     -- 缓存的玩家id数量
    ships            INT          DEFAULT 0,     -- 缓存的船只id总数量
    battles          BIGINT       DEFAULT 0,     -- 缓存船只战斗场次总数
    ranking          INT          DEFAULT 0,     -- 排行榜数据库总行数

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_node_cache 
    (id) 
VALUES
    (1), (2), (3), (4), (5);

-- 子节点缓存数据信息
CREATE TABLE IF NOT EXISTS T_node_db (
    id               TINYINT      PRIMARY KEY,   -- D_region.id

    main_db_tables   INT          DEFAULT 0,     -- 主数据库表数量
    main_db_rows     INT          DEFAULT 0,     -- 主数据库总行数（不包括暂存表和排行榜表）
    main_db_size     BIGINT       DEFAULT 0,     -- 主数据库占用空间（kb）
    snapshot_files   INT          DEFAULT 0,     -- 快照文件数量
    snapshot_size    BIGINT       DEFAULT 0,     -- 快照文件占用空间（kb）

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_node_db
    (id)
VALUES
    (1), (2), (3), (4), (5);

-- 子节点用户活跃度分布（lv_0 ~ lv_9）
CREATE TABLE IF NOT EXISTS T_node_user_activity (
    id               TINYINT      PRIMARY KEY,   -- D_region.id

    lv_0             INT          DEFAULT 0,
    lv_1             INT          DEFAULT 0,
    lv_2             INT          DEFAULT 0,
    lv_3             INT          DEFAULT 0,
    lv_4             INT          DEFAULT 0,
    lv_5             INT          DEFAULT 0,
    lv_6             INT          DEFAULT 0,
    lv_7             INT          DEFAULT 0,
    lv_8             INT          DEFAULT 0,
    lv_9             INT          DEFAULT 0,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_node_user_activity
    (id)
VALUES
    (1), (2), (3), (4), (5);

-- 子节点工会活跃度分布（lv_0 ~ lv_3）
CREATE TABLE IF NOT EXISTS T_node_clan_activity (
    id               TINYINT      PRIMARY KEY,   -- D_region.id

    lv_0             INT          DEFAULT 0,
    lv_1             INT          DEFAULT 0,
    lv_2             INT          DEFAULT 0,
    lv_3             INT          DEFAULT 0,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_node_clan_activity
    (id)
VALUES
    (1), (2), (3), (4), (5);