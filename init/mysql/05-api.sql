CREATE TABLE IF NOT EXISTS T_api_token (
    id               INT          AUTO_INCREMENT,

    token            VARCHAR(64)  DEFAULT NULL,

    role_root        BOOLEAN      DEFAULT FALSE,
    role_bot         BOOLEAN      DEFAULT FALSE,
    role_rank        BOOLEAN      DEFAULT FALSE,
    
    source           VARCHAR(64)  DEFAULT NULL,

    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE INDEX idx_token (token)
);