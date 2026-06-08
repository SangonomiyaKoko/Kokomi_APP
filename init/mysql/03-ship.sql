CREATE TABLE IF NOT EXISTS T_ship_base (
    id               TINYINT      PRIMARY KEY,

    corporation      VARCHAR(10)  NOT NULL,         -- 开发商
    name_version     VARCHAR(10)  DEFAULT NULL,     -- 船只名称版本
    ship_count       INT          DEFAULT 0,        -- 船只数量（不包括不可用船只）

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO T_ship_base 
    (id, corporation) 
VALUES
    (1, 'wg'), (2, 'lesta');


-- 船只基础信息表
CREATE TABLE IF NOT EXISTS T_ship_info (
    id               INT          AUTO_INCREMENT,

    corporation_id   TINYINT      NOT NULL,         -- T_ship_base.id
    ship_id          BIGINT       NOT NULL,         -- 1-11位的非连续数字

    is_enabled       BOOLEAN      DEFAULT FALSE,    -- 是否启用统计
    is_old           BOOLEAN      DEFAULT FALSE,    -- 是否为旧船
    tier             TINYINT      DEFAULT 1,        -- 船只等级 1-11
    type_id          TINYINT      DEFAULT 1,        -- D_ship_type.id
    nation_id        TINYINT      DEFAULT 1,        -- D_ship_nation.id
    rarity_id        TINYINT      DEFAULT NULL,     -- D_ship_rarity.id
    premium          BOOLEAN      DEFAULT FALSE,    -- 是否为金币船
    special          BOOLEAN      DEFAULT FALSE,    -- 是否为特种船
    index_code       VARCHAR(10)  DEFAULT NULL,     -- 索引代码

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX idx_tier (corporation_id, tier),
    INDEX idx_type (corporation_id, type_id),
    INDEX idx_nation (corporation_id, nation_id),
    UNIQUE INDEX idx_sid (corporation_id, is_enabled, is_old, ship_id)
);

-- 船只名称表
CREATE TABLE IF NOT EXISTS T_ship_name (
    id               INT          AUTO_INCREMENT,

    corporation_id   TINYINT      NOT NULL,         -- T_ship_base.id
    ship_id          BIGINT       NOT NULL,         -- 1-11位的非连续数字

    zh_cn            VARCHAR(50)  DEFAULT NULL,     -- 中文（国服和谐）
    zh_sg            VARCHAR(50)  DEFAULT NULL,     -- 简体中文
    zh_tw            VARCHAR(50)  DEFAULT NULL,     -- 繁体中文
    en_short         VARCHAR(50)  DEFAULT NULL,     -- 英文（简称）
    en_full          VARCHAR(50)  DEFAULT NULL,     -- 英文（全称）
    ja               VARCHAR(50)  DEFAULT NULL,     -- 日文
    ru               VARCHAR(50)  DEFAULT NULL,     -- 俄文
    verify           BOOLEAN      DEFAULT FALSE,    -- 是否已验证（俄服特有）

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE INDEX idx_sid (corporation_id, ship_id)
);

-- 船只别名称表（中文）
CREATE TABLE IF NOT EXISTS T_ship_nickname_zh (
    id               INT          AUTO_INCREMENT,

    corporation_id   TINYINT      NOT NULL,         -- T_ship_base.id
    ship_id          BIGINT       NOT NULL,         -- 1-11位的非连续数字

    name_1           VARCHAR(20)  DEFAULT NULL,     -- 别名
    name_2           VARCHAR(20)  DEFAULT NULL,     -- 别名
    name_3           VARCHAR(20)  DEFAULT NULL,     -- 别名
    name_4           VARCHAR(20)  DEFAULT NULL,     -- 别名
    name_5           VARCHAR(20)  DEFAULT NULL,     -- 别名

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE INDEX idx_sid (corporation_id, ship_id)
);