from api.loggers import ExceptionLogger
from api.response import JSONResponse
from api.middlewares import MySQLManager


class ShipModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_ship_info_by_id(region_id: int, ship_ids: list[int], language: str):
        async with MySQLManager.read_only_cursor() as cur:
            if region_id == 4:
                corporation_id = 2
            else:
                corporation_id = 1

            language_field = {
                'zh_sg': 'zh_sg',
                'zh_cn': 'zh_cn',
                'en': 'en_short',
                'ja': 'ja',
                'ru': 'ru'
            }.get(language, 'en_short')

            # 构建 IN 子句，用占位符
            placeholders = ','.join(['%s'] * len(ship_ids))
            sql = f"""
                SELECT
                    b.ship_id,
                    b.tier,
                    t.name AS type,
                    n.name AS nation,
                    r.name AS rarity,
                    b.premium, 
                    b.special, 
                    b.index_code,
                    a.{language_field} 
                FROM
                    T_ship_info b
                INNER JOIN D_ship_type t
                    ON b.type_id = t.id
                INNER JOIN D_ship_nation n
                    ON b.nation_id = n.id
                LEFT JOIN D_ship_rarity r
                    ON b.rarity_id = r.id
                LEFT JOIN T_ship_name a
                    ON b.corporation_id = a.corporation_id 
                    AND b.ship_id = a.ship_id
                WHERE b.corporation_id = %s 
                  AND b.ship_id IN ({placeholders})
            """
            params = [corporation_id] + ship_ids
            await cur.execute(sql, params)
            rows = await cur.fetchall()

            # 构建 ship_id -> data 的映射
            result = {}
            for row in rows:
                if not row:
                    continue
                result[row[0]] = {
                    'tier': row[1],
                    'type': row[2],
                    'nation': row[3],
                    'rarity': row[4],
                    'is_premium': True if row[5] else False,
                    'is_special': True if row[6] else False,
                    'index': row[7],
                    'name': row[8]
                }
            return JSONResponse.success(result)
      