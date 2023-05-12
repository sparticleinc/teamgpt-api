import asyncio
import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from teamgpt.schemata import SendWsData
from teamgpt.util.ws import manager

router = APIRouter(prefix='/api/v1/ws', tags=['ws'])


# 测试发送消息
@router.post('/send/{channel}')
async def send(channel: str, input_send: SendWsData):
    return await manager.broadcast(json.dumps(input_send.dict()), channel)


@router.websocket("/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    await manager.connect(websocket, channel)
    await manager.broadcast(
        json.dumps(SendWsData(
            type='join',
            client_id=websocket.client.host,
            timestamp=int(time.time()),
            data={}
        ).dict()), channel
    )

    async def heartbeat():
        while True:
            try:
                await asyncio.sleep(60)
                await websocket.send_text(json.dumps(SendWsData(
                    type='ping',
                    client_id='server',
                    timestamp=int(time.time()),
                    data={}
                ).dict()))
            except WebSocketDisconnect:
                break

    # 启动计时器
    asyncio.create_task(heartbeat())

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"send: {data}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        await manager.broadcast(json.dumps(SendWsData(
            type='leave',
            client_id=websocket.client.host,
            timestamp=int(time.time()),
            data={}
        ).dict()), channel)
    except Exception as e:
        print(f"WebSocket连接异常：{e}")
        manager.disconnect(websocket, channel)
        await manager.broadcast(json.dumps(SendWsData(
            type='leave_abnormal',
            client_id=websocket.client.host,
            timestamp=int(time.time()),
            data={}
        ).dict()), channel)
