import json
from tqdm import tqdm
from redis import Redis
from typing import Any, Iterator

from logger import TqdmAwareLogger, logger
from utils import get_formatted_date, load_msgpack_to_dict
from settings import (
    TEMP_DIR,
    USE_TQDM

)


def progress_iterable(
    items: list[Any], desc: str, logger_obj: TqdmAwareLogger
) -> Iterator[Any]:
    """遍历列表，tqdm 模式下用进度条，否则日志输出进度。

    Args:
        items: 待遍历的列表。
        desc: 进度描述文本。
        logger_obj: TqdmAwareLogger 实例。

    Yields:
        列表中的每个元素。
    """
    if USE_TQDM:
        tqdm_desc = f'{get_formatted_date()} [INFO] {desc}'
        with tqdm(items, desc=tqdm_desc, total=len(items)) as pbar:
            for item in pbar:
                pbar.set_postfix_str(str(item))
                yield item
    else:
        total = len(items)
        for idx, item in enumerate(items, 1):
            logger_obj.info('%s - [%d/%d] | Current: %s', desc, idx, total, item)
            yield item

def clan_ranking(redis_client: Redis):
    season_id = 0
    total_clans = []
    total_count = 0

    for region in ['asia','eu','na','ru','cn']:
        msgpack_file_path = TEMP_DIR / f'clan_ranking_{region}.msgpack'
        data = load_msgpack_to_dict(msgpack_file_path)
        if data is None or data.get('data', []) == []:
            continue

        logger.info(f"Processing clan cache: {region} - {data['season']} - {data['clans']}")

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
    now_date = get_formatted_date()[:10]
    total_ships = {}
    total_count = {}
    ship_limit = {}

    for region in ['asia','eu','na','ru','cn']:
        msgpack_file_path = TEMP_DIR / f'ship_ranking_{region}.msgpack'
        data = load_msgpack_to_dict(msgpack_file_path)
        if data is None or data.get('data', {}) == {}:
            continue

        users_top = {}
        region_users = 0
        update_time = data['time']

        for ship_id in progress_iterable(
            items=data.get('data', {}).keys(), 
            desc=f"Processing ship - {region}",
            logger_obj=logger
        ):
            ship_data = data.get('data', {}).get(ship_id)
            if ship_data is None:
                continue
            
            archieve_data = {}

            cache_data = {
                'meta': {
                    'region': region,
                    'time': update_time,
                    'limit': ship_data['limit'],
                    'users': ship_data['users']
                },
                'rows': []
            }

            if region != 'ru' and ship_id not in ship_limit:
                ship_limit[ship_id] = ship_data['limit']

            for user in ship_data['rows']:
                account_id = user[1]
                cache_data['rows'].append([
                    user[0], region, user[1], user[2], user[3], user[4], 
                    user[5], int(user[6]), user[7],  user[9], 
                    user[11], user[13], user[14], user[8], 
                    user[10], user[12], user[15], user[16]
                ])
                archieve_data[user[1]] = user[0]

                if account_id not in users_top:
                    region_users += 1
                    users_top[account_id] = {
                        'username': user[4],
                        'clan_tag': user[2],
                        'league': user[3],
                        'rows': []
                    }
                users_top[account_id]['rows'].append([
                    int(ship_id), user[0], ship_data['users'],
                    user[5], int(user[6]), user[7], user[9],
                    user[11], user[13], user[8], user[10],
                    user[12],
                ])

            key = f'ranking:ship:{region}:{ship_id}'
            redis_client.set(key, json.dumps(cache_data))
            key = f'ship_archieve:{now_date}:{region}:{ship_id}'
            redis_client.set(key, json.dumps(archieve_data), ex=31*86400)

            if region == 'ru':
                continue

            if ship_id not in total_ships:
                total_ships[ship_id] = []
                total_count[ship_id] = 0

            total_count[ship_id] += ship_data['users']

            for user in ship_data['rows']:
                total_ships[ship_id].append([region] + user[1:])

        for account_id in progress_iterable(
            items=users_top.keys(), 
            desc=f"Processing user - {region}",
            logger_obj=logger
        ):
            user_data = users_top.get(account_id)
            if user_data is None:
                continue
            key = f'ranking:user:{region}:{account_id}'
            redis_client.set(key, json.dumps(user_data), 4*3600)
    
    for ship_id in progress_iterable(
        items=total_ships.keys(), 
        desc=f"Processing ship - all",
        logger_obj=logger
    ):
        total_users = total_ships.get(ship_id)
        if total_users is None:
            continue
        
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
            cache_data['rows'].append([
                rank + 1, user[0], user[2], user[3],
                user[4], user[5], int(user[6]),
                user[7], user[9], user[11], user[13],
                user[14], user[8], user[10], user[12],
                user[15], user[16]
            ])
        key = f'ranking:ship:all:{ship_id}'
        redis_client.set(key, json.dumps(cache_data))