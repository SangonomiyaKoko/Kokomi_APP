#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import threading
from contextlib import asynccontextmanager
from starlette.responses import StreamingResponse
from fastapi import FastAPI, Request, HTTPException, Header

from api.core import EnvConfig, api_logger
from api.middlewares import AuthManager
from api.response import JSONResponse
from api.utils import TimeUtils
from api.loggers import CSVWriter, log_queue
from api.middlewares import (
    MySQLManager,
    RedisClient,
    RedisConnection
)
from api.network import NodeManager
from api.routers import (
    bot_router,
    manager_router,
    search_router,
    external_router,
    ranking_router
)

# 后台日志写入线程，用于将日志队列中的请求信息写入CSV文件
def csv_writer_thread():
    writer = CSVWriter()
    api_logger.info('The log writing thread has been started')
    while True:
        record = log_queue.get()
        api_logger.debug('Received a log data to be written')
        if record is None:  # 退出信号
            break
        writer.write(record)
        log_queue.task_done()

    writer.close()
    api_logger.info('The log writing thread has exited')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 读取工作路径
    ROOT_DIR = os.getcwd()
    api_logger.info(f'Working dir: {ROOT_DIR}')
    # 从环境中加载配置
    env_file = EnvConfig.init(ROOT_DIR)
    if env_file:
        api_logger.info(f"Env config loaded: {env_file}")
    else:
        api_logger.error("Env config load failed")
    # 启动API日志写入线程
    writer_thread = threading.Thread(target=csv_writer_thread, daemon=True)
    writer_thread.start()
    # 初始化并测试redis连接
    await RedisConnection.init_conn()
    await RedisConnection.test_redis()
    # 初始化mysql并测试mysql连接
    await MySQLManager.init_pool()
    await MySQLManager.test_connection()

    tokens_data = await MySQLManager.load_token()
    nodes_data = await MySQLManager.load_node_info()
    AuthManager.init(tokens_data)
    node_client = httpx.AsyncClient()
    await NodeManager.init(nodes_data, node_client)

    try:
        yield
    finally:
        await NodeManager.close()
        await MySQLManager.close_pool()
        await RedisConnection.close_redis()
        # 发送退出信号，等待剩下数据写入并退出线程
        log_queue.put(None)
        writer_thread.join()


app = FastAPI(lifespan=lifespan)


# 请求中间件
@app.middleware("http")
async def request_rate_limiter(request: Request, call_next):
    # client_ip = request.client.host if request.client else None
    # if client_ip != '127.0.0.1':
    #     return JSONResponse(
    #         status_code=403,
    #         content={"detail": "Forbidden"}
    #     )
    start = TimeUtils.timestamp_ms()
    now_time = TimeUtils.now_iso()
    try:
        await RedisClient.api_record(now_time[:10])
    except Exception:
        pass
    response: StreamingResponse = await call_next(request)
    elapsed = int((TimeUtils.timestamp_ms() - start))
    record = [
        now_time,
        request.client.host if request.client else "-",
        request.method,
        request.url,
        response.status_code,
        elapsed
    ]
    try:
        log_queue.put_nowait(record)
    except Exception:
        api_logger.warning('Log queue full')
        pass  # 队列满时直接丢弃，避免阻塞接口
    return response


@app.get("/", summary="Home", tags=["Default"])
async def root():
    """测试接口连通性"""
    return JSONResponse.API_1000_Success

@app.get("/token/permissions/", summary="Get Token Permissions", tags=["Auth"])
async def get_token_permissions(
    assess_token: str = Header(..., alias="assess-token"),
):
    """查询当前 assess-token 所拥有的权限列表

    从请求头 ``assess-token`` 中提取 token，
    返回该 token 持有的所有权限名称。
    """
    permissions = AuthManager.get_permissions(assess_token)
    if permissions is None:
        raise HTTPException(
            status_code=403,
            detail='Invalid Access Token',
        )
    return JSONResponse.success(
        data={"permissions": list(permissions)}
    )

app.include_router(
    manager_router,
    prefix="/api",
    tags=["Manager Interface"],
)

app.include_router(
    external_router,
    prefix="/api",
    tags=["External Interface"],
)

app.include_router(
    bot_router,
    prefix="/api",
    tags=["Bot Interface"],
)

app.include_router(
    search_router,
    prefix="/api",
    tags=["Search Interface"],
)

app.include_router(
    ranking_router,
    prefix="/api",
    tags=["Ranking Interface"],
)