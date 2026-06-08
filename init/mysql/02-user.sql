-- 用户绑定信息列表
CREATE TABLE IF NOT EXISTS T_user_base (
    id               BIGINT       AUTO_INCREMENT,

    region_id        TINYINT      NOT NULL,
    account_id       BIGINT       NOT NULL,
    username         VARCHAR(25)  NOT NULL,
    register_time    TIMESTAMP    DEFAULT NULL,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX idx_rid_aid (region_id, account_id)
);

-- 用户基本信息表
CREATE TABLE IF NOT EXISTS T_user_info (
    id               INT          AUTO_INCREMENT,  -- 用户在系统中的 UID

    platform_id      TINYINT      NOT NULL,   -- D_platform.id
    platform_uid     VARCHAR(64)  NOT NULL,   -- platform user id

    -- 用户信息
    username         VARCHAR(64)  DEFAULT NULL,   -- 用户名称
    avatar           VARCHAR(100) DEFAULT NULL,   -- 用户头像
    points           INT          DEFAULT 0,      -- 查询点数

    -- 绑定信息
    binding_id       INT          DEFAULT NULL,   -- 当前绑定的账号 T_user_base.id
    binding_ids      VARCHAR(64)  DEFAULT NULL,   -- 绑定账号列表

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE KEY uk_platform_user (platform_id, platform_uid)
);