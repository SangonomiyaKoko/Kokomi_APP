from typing import List, Dict, Any
from dataclasses import dataclass, field

from api.response import JSONResponse
from api.utils import GameUtils, TimeUtils
from api.models import ShipModel
from api.middlewares import RedisClient
from api.loggers import ExceptionLogger
from api.network import NodeAPI, NodeManager


@dataclass
class UserLeaderboardResponse:
    '''排行榜响应数据结构'''
    basic: Dict[str, Any] = field(default_factory=dict)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    credits: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'basic': self.basic,
            'rows': self.rows,
            'credits': self.credits
        }

class UserRankingAPI:
    def _format_ranking_rows(row: dict, ship: dict):
        return {
            'rank': row[0],
            'users': row[1],
            'battles': str(row[2]),
            'win_rate': str(row[4]) + '%',
            'rating': row[3],
            'avg_damage': '{:,}'.format(row[5]).replace(',', ' '),
            'avg_frags': str(row[6]),
            'avg_exp': '{:,}'.format(row[7]).replace(',', ' '),
            'level': {
                'win_rate': row[8],
                'avg_damage': row[9],
                'avg_frags': row[10]
            },
            'ship': {
                'tier': str(ship['tier']),
                'type': ship['type'],
                'nation': ship['nation'],
                'is_premium': ship['is_premium'],
                'is_special': ship['is_special'],
                'index': ship['index'],
                'name': ship['name']
            }
        }
    
    @ExceptionLogger.handle_program_exception_async
    async def refresh_user(
        region_id: int, 
        user_id: int
    ):
        # 获取子节点信息，不可用则直接返回
        node = NodeManager.get_node(region_id)
        if node is None:
            return JSONResponse.API_NodeNotAvailable

        path = f"/api/platform/user/{user_id}/"
        params = {}

        error, refresh = JSONResponse.extract_data(
            response=await NodeAPI.patch(node, path, params)
        )
        if error:
            return refresh
    
    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def get_user_ranking(
        cls,
        credits: int,
        region_id: int,
        user_id: int,
        language: str
    ):
        region = GameUtils.get_region(region_id)
        key = f'ranking:user:{region}:{user_id}'

        error, ranking = JSONResponse.extract_data(
            response=await RedisClient.get(key)
        )
        if error:
            return ranking
        
        if not ranking:
            return JSONResponse.API_1000_Success
        
        sort_list = []
        cache_data = {}
        for row in ranking['rows']:
            sort_list.append([row[0], row[1]])
            cache_data[row[0]] = row[1:]

        error, ships_info = JSONResponse.extract_data(
            response=await ShipModel.get_ship_info_by_id(region_id, [s[0] for s in sort_list], language)
        )
        if error:
            return ships_info
        
        sorted_data = sorted(
            sort_list,
            key=lambda x: x[1]
        )

        result = UserLeaderboardResponse(
            basic={
                'username': ranking['username'],
                'clan_tag': ranking['clan_tag'],
                'league': ranking['league']
            },
            rows=[],
            credits=credits
        )

        for ship_id, _ in sorted_data:
            ship_data = ships_info.get(ship_id)
            if ship_data is None:
                continue
            user_row = cache_data.get(ship_id)
            if user_row is None:
                continue
            result.rows.append(cls._format_ranking_rows(user_row, ship_data))

        return JSONResponse.success(result.to_dict())