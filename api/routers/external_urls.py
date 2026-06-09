from fastapi import APIRouter, Depends, Path, Query

from api.middlewares import require_permission
from api.schemas import Region
from api.utils import GameUtils
from api.apis.external import ExternalRankingAPI, ExternalStatsAPI

router = APIRouter(prefix="/external")


@router.get("/ship-ranking/{region}/{ship_id}/",summary="服务器船只排行榜")
async def getShipTop(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器"),
    ship_id: int = Path(..., description="船只ID"),
    page_index: int = Query(1, description="页索引"),
    page_size: int = Query(50, description="页大小"),
    dogtag: int = Query(0, description="是否返回用户的dogtag数据")
):
    """获取指定page页的船只排行榜数据

    该功能基于用户在本地的缓存数据进行计算，因此和最新数据存在不同步情况，如需更新可以通过后续接口进行刷新

    如果某个船只不符合条件或者没有排行榜数据则返回的 data 为空 List[]

    船只排行榜上榜条件：
    1. 船只等级大于5级
    2. 船只统计到一定场次的数据
    3. 用户未被平台拉黑

    level -> color：指标 1-8 分别对应还需努力-神佬平均这八个评级（0表示水平未知，但是理论上不应该出现）

    ⚠️ 关于子节点维护的特别说明：

    为确保缓存数据的一致性以及可能的更新需求，子节点会存在停服更新的情况，此时服务器会返回该结果：

    {"status": "ok","code": 1101,"message": "NodeNotAvailable"}
    
    ⚠️ 关于隐藏战绩用户的特别说明：

    某个用户隐藏战绩，系统默认不会删除缓存中的数据，因此依然会参加统计
    """
    region_id = GameUtils.get_region_id(region.value)
    return await ExternalRankingAPI.get_ship_top(region_id, ship_id, page_index, page_size, dogtag)


@router.get("/user-refresh/{region}/{user_id}/",summary="刷新用户缓存数据")
async def refreshUser(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器"),
    user_id: int = Path(..., description="用户ID")
):
    """手动触发刷新用户的缓存数据

    ⚠️ 该接口 data 中不会携带任何数据，code=1000即可视为刷新成功
    
    该指令会调用接口更新用户的基本信息（名称，工会，徽章等），同时将该用户标记为缓存待刷新状态

    后台的缓存刷新服务器会每隔 10 分钟刷新一次，并同步更新排行榜数据
    """
    region_id = GameUtils.get_region_id(region.value)
    return await ExternalRankingAPI.refresh_user(region_id, user_id)


@router.get("/ship-stats/{region}/",summary="获取船只的服务器数据")
async def getShipStats(
    _: str = Depends(require_permission("rank")),
    region: Region = Path(..., description="服务器")
):
    """获取指定服务器下船只的服务器数据

    该数据为船只的场次平均数据而非用户平均数据，仅返回有数据的船只
    """
    region_id = GameUtils.get_region_id(region.value)
    return await ExternalStatsAPI.get_ship_stats(region_id)