INSERT INTO region 
    (id, name) 
VALUES
    (1, 'asia'),
    (2, 'eu'),
    (3, 'na'),
    (4, 'ru'),
    (5, 'cn');

INSERT INTO platform 
    (id, name) 
VALUES
    (1, 'qq_bot'),
    (2, 'qq_group'),
    (3, 'qq_guild'),
    (4, 'discord');

INSERT INTO clan_battle_season
    (season_id, season_start, season_finish)
VALUES 
    (32, FROM_UNIXTIME(1764568800), FROM_UNIXTIME(1770616800));

INSERT INTO api_token
    (token, permission, extra)
VALUES
    ('root', 'root', 'DefaultRootToken'),
    ('user', 'user', 'DefaultUserToken');