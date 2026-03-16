CREATE DATABASE IF NOT EXISTS wows_main_db;

USE wows_main_db;



/* 基础字典表 */

CREATE TABLE D_region (
    id           TINYINT UNSIGNED PRIMARY KEY COMMENT '区域ID',
    name         VARCHAR(10)  NOT NULL        COMMENT '区域名称',
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT='游戏区域基础数据表';


CREATE TABLE D_platform (
    id           TINYINT UNSIGNED PRIMARY KEY COMMENT '平台ID',
    name         VARCHAR(10)  NOT NULL        COMMENT '平台名称',
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT='用户来源平台定义表';



/* Clan Battle 赛季信息 */

-- 该表仅保存当前赛季信息，理论上始终只有一条数据
CREATE TABLE T_clan_battle_season (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',

    season_id       INT       NOT NULL COMMENT '赛季ID',
    season_start    TIMESTAMP NOT NULL COMMENT '赛季开始时间',
    season_finish   TIMESTAMP NOT NULL COMMENT '赛季结束时间',

    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='Clan Battle 当前赛季元数据';

CREATE TABLE T_clan_battle_stats (
    id                     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',

    region_id              TINYINT UNSIGNED NOT NULL     COMMENT '区域ID',
    clan_id                BIGINT  UNSIGNED NOT NULL     COMMENT '工会ID',

    season                 TINYINT UNSIGNED DEFAULT 0    COMMENT '赛季ID',
    battles_count          INT UNSIGNED     DEFAULT 0    COMMENT '总战斗场次',
    public_rating          INT              DEFAULT 1100 COMMENT '工会评分',
    league                 TINYINT UNSIGNED DEFAULT 4    COMMENT '段位 0=紫金 1=白金 2=黄金 3=白银 4=青铜',
    division               TINYINT UNSIGNED DEFAULT 2    COMMENT '分段 1/2/3',
    division_rating        INT              DEFAULT 0    COMMENT '当前分段积分',

    longest_winning_streak INT UNSIGNED     DEFAULT 0    COMMENT '最长连胜',
    last_battle_at         TIMESTAMP NULL DEFAULT NULL   COMMENT '最近一场战斗时间',

    team_data              VARCHAR(100) DEFAULT NULL     COMMENT '队伍数据快照',
    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                           ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE KEY uk_region_clan (region_id, clan_id),
    INDEX idx_last_battle (last_battle_at)
) COMMENT='工会当前赛季统计数据';

-- 指定赛季战斗记录（示例：S33）
-- 当更新 clan_battle_season 时会有相应代码自动创建对应赛季表
CREATE TABLE T_clan_battle_s33 (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',

    battle_time     TIMESTAMP NOT NULL            COMMENT '战斗结束时间',
    region_id       TINYINT UNSIGNED NOT NULL     COMMENT '区域ID',
    clan_id         BIGINT  UNSIGNED NOT NULL     COMMENT '工会ID',
    team_number     TINYINT UNSIGNED NOT NULL     COMMENT '队伍编号 1=Alpha 2=Bravo',

    battle_result   VARCHAR(10) NOT NULL          COMMENT '结果 victory/defeat',
    battle_rating   VARCHAR(10) DEFAULT NULL      COMMENT '评分变化（NULL表示晋级/保级赛阶段）',
    battle_stage    VARCHAR(10) DEFAULT NULL      COMMENT '晋级/保级赛结果（+★ / +☆）',

    league          TINYINT UNSIGNED DEFAULT NULL COMMENT '结算段位',
    division        TINYINT UNSIGNED DEFAULT NULL COMMENT '结算分段',
    division_rating INT              DEFAULT NULL COMMENT '结算分段积分',
    public_rating   INT              DEFAULT NULL COMMENT '结算公开评分',

    stage_type      VARCHAR(10) DEFAULT NULL      COMMENT '晋级赛类型',
    stage_progress  VARCHAR(50) DEFAULT NULL      COMMENT '晋级赛进度',

    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',

    INDEX idx_battle_time (battle_time),
    INDEX idx_region_clan (region_id, clan_id)
) COMMENT='Clan Battle S33赛季战斗记录';



/* 用户绑定系统 */

CREATE TABLE T_user_binding (
    id                   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',

    platform_id          TINYINT UNSIGNED NOT NULL     COMMENT '来源平台ID',
    platform_user_id     VARCHAR(64) NOT NULL          COMMENT '平台侧用户唯一ID',

    binding_region_id    TINYINT UNSIGNED DEFAULT NULL COMMENT '当前绑定区域',
    binding_account_id   INT UNSIGNED     DEFAULT NULL COMMENT '当前绑定游戏账号ID',

    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                         ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE KEY uk_platform_user (platform_id, platform_user_id),

    CONSTRAINT fk_binding_platform
        FOREIGN KEY (platform_id)
        REFERENCES platform(id)
        ON DELETE RESTRICT
) COMMENT='平台用户绑定主表';

CREATE TABLE T_user_bind_account (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',

    user_id     INT UNSIGNED     NOT NULL COMMENT '对应 user_binding.id',
    region_id   TINYINT UNSIGNED NOT NULL COMMENT '游戏区域',
    account_id  INT UNSIGNED     NOT NULL COMMENT '游戏账号ID',

    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',

    UNIQUE KEY uk_user_region_account (user_id, region_id, account_id),
    INDEX idx_user_id (user_id),

    CONSTRAINT fk_bind_account_user
        FOREIGN KEY (user_id)
        REFERENCES user_binding(id)
        ON DELETE CASCADE
) COMMENT='用户绑定游戏账号列表';



/* API系统相关基础表 */

CREATE TABLE T_platform_blacklist (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键',

    target_type   TINYINT UNSIGNED NOT NULL   COMMENT '封禁类型 1=IP 2=USER 3=CLAN',
    target_value  VARCHAR(64) NOT NULL        COMMENT '封禁目标值',

    reason        VARCHAR(255) DEFAULT NULL   COMMENT '封禁原因',
    expires_at    TIMESTAMP NULL DEFAULT NULL COMMENT '过期时间（NULL=永久封禁）',

    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    UNIQUE KEY uk_type_value (target_type, target_value),
    INDEX idx_expires_at (expires_at)
) COMMENT='系统黑名单表';

CREATE TABLE T_platform_token (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键',

    token         VARCHAR(128) NOT NULL       COMMENT '访问令牌',
    permission    VARCHAR(32)  NOT NULL       COMMENT '权限等级 root/user',

    extra         VARCHAR(255) DEFAULT NULL   COMMENT '备注信息',
    expires_at    TIMESTAMP NULL DEFAULT NULL COMMENT '过期时间（NULL=长期有效）',

    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    UNIQUE KEY uk_token (token)
) COMMENT='API访问令牌表';