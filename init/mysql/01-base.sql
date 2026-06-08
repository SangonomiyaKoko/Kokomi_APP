-- 定义 region_id 对应的 region 字段
CREATE TABLE IF NOT EXISTS D_region (
    id               TINYINT      PRIMARY KEY,

    name             VARCHAR(10)  NOT NULL,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO D_region 
    (id, name) 
VALUES
    (1, 'asia'), (2, 'eu'), (3, 'na'), (4, 'ru'), (5, 'cn');

-- 定义 platform_id 对应的 platform 字段
CREATE TABLE IF NOT EXISTS D_platform (
    id               TINYINT      PRIMARY KEY,

    name             VARCHAR(10)  NOT NULL,
    
    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO D_platform 
    (id, name) 
VALUES
    (1, 'qq_bot'), (2, 'qq_group'),  (3, 'qq_guild'), (4, 'discord');

-- 定义船只 type_id 对应的 type 字段
CREATE TABLE IF NOT EXISTS D_ship_type (
    id               TINYINT      PRIMARY KEY,

    name             VARCHAR(20)  NOT NULL,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO D_ship_type 
    (id, name) 
VALUES
    (1, 'AirCarrier'), (2, 'Battleship'), (3, 'Cruiser'), (4, 'Destroyer'), (5, 'Submarine');

-- 定义船只 nation_id 对应的 nation 字段
CREATE TABLE IF NOT EXISTS D_ship_nation (
    id               TINYINT      PRIMARY KEY,

    name             VARCHAR(20)  NOT NULL,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO D_ship_nation 
    (id, name) 
VALUES
    (1, 'usa'), (2, 'japan'), (3, 'germany'), (4, 'uk'), (5, 'ussr'), 
    (6, 'france'), (7, 'italy'), (8, 'pan_asia'), (9, 'europe'), 
    (10, 'netherlands'), (11, 'commonwealth'), (12, 'pan_america'), (13, 'spain');

-- 定义船只 rarity_id 对应的 rarity 字段
CREATE TABLE IF NOT EXISTS D_ship_rarity (
    id               TINYINT      PRIMARY KEY,

    name             VARCHAR(20)  NOT NULL,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO D_ship_rarity 
    (id, name) 
VALUES
    (1, 'Common'), (2, 'Uncommon'), (3, 'Rare'), (4, 'Epic'), (5, 'Legendary');

CREATE TABLE IF NOT EXISTS T_game_version (
    id               INT          AUTO_INCREMENT,

    corporation_id   TINYINT      NOT NULL,        -- 开发商id
    corporation_name VARCHAR(10)  NOT NULL,        -- 开发商名称
    is_latest        BOOLEAN      DEFAULT FALSE,   -- 是否为最新版本
    game_version     VARCHAR(10)  DEFAULT NULL,    -- 船只名称版本

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    KEY k_cid_ct (corporation_id, created_at)
);