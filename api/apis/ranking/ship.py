from typing import List, Dict, Any
from dataclasses import dataclass, field

from api.response import JSONResponse
from api.utils import GameUtils, TimeUtils
from api.models import ShipModel
from api.middlewares import RedisClient
from api.loggers import ExceptionLogger


@dataclass
class ShipLeaderboardResponse:
    '''排行榜响应数据结构'''
    meta: Dict[str, Any] = field(default_factory=dict)
    ship: Dict[str, Any] = field(default_factory=dict)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    credits: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'meta': self.meta,
            'ship': self.ship,
            'rows': self.rows,
            'credits': self.credits
        }

class ShipRankingAPI:
    def _format_ranking_rows(rows: list, archieve: dict | int):
        result = []
        for row in rows:
            user_id = str(row[2])

            if archieve is None or user_id not in archieve:
                delta = None
            else:
                delta = row[0] - archieve[user_id]

            result.append({
                'rank': str(row[0]),
                'delta': delta,
                'region': row[1],
                'clan_tag': row[3],
                'league': row[4],
                'username': row[5],
                'battles': str(row[6]),
                'rating': row[7],
                'win_rate': str(row[8]) + '%',
                'avg_damage': '{:,}'.format(row[9]).replace(',', ' '),
                'avg_frags': str(row[10]),
                'avg_exp': '{:,}'.format(row[11]).replace(',', ' '),
                'hit_ratio': str(row[12]) + '%',
                'level': {
                    'win_rate': row[13],
                    'avg_damage': row[14],
                    'avg_frags': row[15]
                },
                'max': {
                    'exp': '{:,}'.format(row[16]).replace(',', ' '),
                    'damage': '{:,}'.format(row[17]).replace(',', ' ')
                }
            })
        return result
    
    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def get_ship_ranking(
        cls,
        credits: int,
        region_id: int, 
        ship_id: int,
        language: str
    ):
        region = GameUtils.get_region(region_id)
        key = f'ranking:ship:{region}:{ship_id}'

        error, ranking = JSONResponse.extract_data(
            response=await RedisClient.get(key)
        )
        if error:
            return ranking
        
        if not ranking:
            return JSONResponse.API_1000_Success
        
        now_date = TimeUtils.offset_iso(7, "%Y-%m-%d")
        key = f'ship_archieve:{now_date}:{region}:{ship_id}'

        error, archieve = JSONResponse.extract_data(
            response=await RedisClient.get(key)
        )
        if error:
            return archieve

        error, ships_info = JSONResponse.extract_data(
            response=await ShipModel.get_ship_info_by_id(region_id, [ship_id], language)
        )
        if error:
            return ships_info
        
        ship_info = ships_info.get(ship_id)
        if not ship_info:
            return JSONResponse.API_1000_Success
        
        result = ShipLeaderboardResponse(
            meta={
                'region': ranking['meta']['region'],
                'time': TimeUtils.diff_timestamp(ranking['meta']['time']),
                'limit': str(ranking['meta']['limit']),
                'users': str(ranking['meta']['users'])
            },
            ship={
                'tier': str(ship_info['tier']),
                'type': ship_info['type'],
                'nation': ship_info['nation'],
                'is_premium': ship_info['is_premium'],
                'is_special': ship_info['is_special'],
                'index': ship_info['index'],
                'name': ship_info['name']
            },
            rows=cls._format_ranking_rows(ranking['rows'], archieve),
            credits=credits
        )

        return JSONResponse.success(result.to_dict())