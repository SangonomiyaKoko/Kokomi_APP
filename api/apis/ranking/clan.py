from typing import List, Dict, Any
from dataclasses import dataclass, field

from api.response import JSONResponse
from api.utils import GameUtils, TimeUtils
from api.middlewares import RedisClient
from api.loggers import ExceptionLogger


@dataclass
class ClanLeaderboardResponse:
    '''排行榜响应数据结构'''
    meta: Dict[str, Any] = field(default_factory=dict)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    credits: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'meta': self.meta,
            'rows': self.rows,
            'credits': self.credits
        }

class ClanRankingAPI:
    def _format_ranking_rows(rows: list):
        result = []
        for row in rows:
            result.append({
                'rank': str(row['rank']),
                'region': row['region'],
                'tag': row['tag'],
                'battles': str(row['battles']),
                'win_rate': str(row['win_rate'])+'%',
                'win_rate_level': row['win_rate_level'],
                'league': row['league'],
                'division': row['division'],
                'rating': row['rating'],
                'max_streak': str(row['max_streak']),
                'stage_type': row['stage_type'],
                'stage_progress': row['stage_progress'],
                'last_battle_time': TimeUtils.diff_timestamp(row['last_battle_at'])
            })
        return result

    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def get_clan_ranking(
        cls,
        credits: int,
        region_id: int
    ):
        region = GameUtils.get_region(region_id)
        key = f'ranking:clan:{region}'

        error, ranking = JSONResponse.extract_data(
            response=await RedisClient.get(key)
        )
        if error:
            return ranking
        
        if not ranking:
            return JSONResponse.API_1000_Success
        
        result = ClanLeaderboardResponse(
            meta={
                'region': ranking['meta']['region'],
                'time': TimeUtils.diff_timestamp(ranking['meta']['time']),
                'season': str(ranking['meta']['season']),
                'clans': str(ranking['meta']['clans'])
            },
            rows=cls._format_ranking_rows(ranking['rows']),
            credits=credits
        )

        return JSONResponse.success(result.to_dict())