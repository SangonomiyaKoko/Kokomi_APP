import json
from redis import Redis

from utils import load_msgpack_to_dict
from settings import TEMP_DIR


def clan_ranking(redis_client: Redis):
    season_id = 0
    total_clans = []
    total_count = 0

    for region in ['asia','eu','na','ru','cn']:
        msgpack_file_path = TEMP_DIR / f'clan_ranking_{region}.msgpack'
        data = load_msgpack_to_dict(msgpack_file_path)
        if data is None or data.get('data', []) == []:
            continue

        cache_data = {
            'meta': {
                'region': region,
                'time': data['time'],
                'season': data['season'],
                'clans': data['clans']
            },
            'rows': []
        }
        for clan in data['data']:
            cache_data['rows'].append({
                'rank': clan[0],
                'region': region,
                'tag': clan[2],
                'battles': clan[4],
                'win_rate': clan[5],
                'win_rate_level': clan[6],
                'league': clan[7],
                'division': clan[8],
                'rating': int(clan[9]),
                'max_streak': clan[10],
                'stage_type': clan[11],
                'stage_progress': clan[12],
                'last_battle_at': clan[13]
            })

        key = f'ranking:clan:{region}'
        redis_client.set(key, json.dumps(cache_data))

        # 俄服不参与统计
        if region == 'ru':
            continue

        if data['season'] == season_id:
            pass
        elif data['season'] > season_id:
            season_id = data['season']
            total_clans = []
        else:
            continue

        total_count += data['clans']
        for clan in data['data']:
            total_clans.append([region] + clan[1:])
    
    sorted_data = sorted(
        total_clans,
        key=lambda x: x[9],
        reverse=True
    )[:50]

    cache_data = {
        'meta': {
            'region': 'all',
            'time': None,
            'season': season_id,
            'clans': total_count
        },
        'rows': []
    }
    for rank, clan in enumerate(sorted_data):
        cache_data['rows'].append({
            'rank': rank + 1,
            'region': clan[0],
            'tag': clan[2],
            'battles': clan[4],
            'win_rate': clan[5],
            'win_rate_level': clan[6],
            'league': clan[7],
            'division': clan[8],
            'rating': int(clan[9]),
            'max_streak': clan[10],
            'stage_type': clan[11],
            'stage_progress': clan[12],
            'last_battle_at': clan[13]
        })
    key = f'ranking:clan:all'
    redis_client.set(key, json.dumps(cache_data))

def user_ranking(redis_client: Redis):
    total_ships = {}
    total_count = {}
    ship_limit = {}

    for region in ['asia','eu','na','ru','cn']:
        msgpack_file_path = TEMP_DIR / f'ship_ranking_{region}.msgpack'
        data = load_msgpack_to_dict(msgpack_file_path)
        if data is None or data.get('data', {}) == {}:
            continue

        update_time = data['time']
        users_top = {}
        region_users = 0

        for ship_id, ship_data in data.get('data', {}).items():
            cache_data = {
                'meta': {
                    'region': region,
                    'time': update_time,
                    'limit': ship_data['limit'],
                    'users': ship_data['users']
                },
                'rows': []
            }

            if ship_id not in ship_limit:
                ship_limit[ship_id] = ship_data['limit']

            for user in ship_data['rows']:
                account_id = user[1]
                cache_data['rows'].append({
                    'rank': user[0],  # 计算实际排名
                    'clan_tag': user[2],
                    'league': user[3],
                    'username': user[4],
                    'battles': user[5],
                    'rating': user[6],
                    'win_rate': user[8],
                    'avg_damage': user[10],
                    'avg_frags': user[12],
                    'avg_exp': user[14],
                    'hit_ratio': user[15],
                    'level': {
                        'rating': user[7],
                        'win_rate': user[9],
                        'avg_damage': user[11],
                        'avg_frags': user[13]
                    },
                    'max': {
                        'exp': user[16],
                        'damage': user[17]
                    }
                })

                # if account_id not in users_top:
                #     region_users += 1
                #     users_top[account_id] = {
                #         'username': user[4],
                #         'clan_tag': user[2],
                #         'league': user[3],
                #         'score': 0,
                #         'ships': 0,
                #         'rows': []
                #     }
                # users_top[account_id]['ships'] += 1
                # users_top[account_id]['score'] += 50 - user[0] + 1
                # users_top[account_id]['rows'].append({
                #     'ship_id': int(ship_id),
                #     'rank': user[0],
                #     'battles': user[5],
                #     'rating': user[6],
                #     'win_rate': user[8],
                #     'avg_damage': user[10],
                #     'avg_frags': user[12],
                #     'avg_exp': user[14],
                #     'level': {
                #         'rating': user[7],
                #         'win_rate': user[9],
                #         'avg_damage': user[11],
                #         'avg_frags': user[13]
                #     }
                # })

            key = f'ranking:ship:{region}:{ship_id}'
            redis_client.set(key, json.dumps(cache_data))

            if region == 'ru':
                continue

            if ship_id not in total_ships:
                total_ships[ship_id] = []
                total_count[ship_id] = 0

            total_count[ship_id] += ship_data['users']

            for user in ship_data['rows']:
                total_ships[ship_id].append([region] + user[1:])
        # for account_id, user_data in users_top.items():
        #     key = f'ranking:user:{region}:{account_id}'
        #     redis_client.set(key, json.dumps(user_data), 2*3600)
    
    for ship_id, total_users in total_ships.items():
        sorted_data = sorted(
            total_users,
            key=lambda x: x[6],
            reverse=True
        )[:50]

        cache_data = {
            'meta': {
                'region': 'all',
                'time': None,
                'limit': ship_limit.get(ship_id, 40),
                'users': total_count.get(ship_id, 0)
            },
            'rows': []
        }
        for rank, user in enumerate(sorted_data):
            cache_data['rows'].append({
                'rank': rank + 1,
                'region': user[0],
                'clan_tag': user[2],
                'league': user[3],
                'username': user[4],
                'battles': user[5],
                'rating': user[6],
                'win_rate': user[8],
                'avg_damage': user[10],
                'avg_frags': user[12],
                'avg_exp': user[14],
                'hit_ratio': user[15],
                'level': {
                    'rating': user[7],
                    'win_rate': user[9],
                    'avg_damage': user[11],
                    'avg_frags': user[13]
                },
                'max': {
                    'exp': user[16],
                    'damage': user[17]
                }
            })
        key = f'ranking:ship:all:{ship_id}'
        redis_client.set(key, json.dumps(cache_data))