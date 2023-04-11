import json
import time
import uuid

from fastapi import APIRouter, Depends, Security, HTTPException, Request
from fastapi_auth0 import Auth0User
from sse_starlette import EventSourceResponse

from teamgpt.models import OpenGptKey, OpenGptChatMessage
from teamgpt.schemata import OpenGptKeyIn, OpenGptKeyOut, OpenGptChatMessageIn
from teamgpt.settings import auth
from teamgpt.util.gpt import ask_open

router = APIRouter(prefix='/open', tags=['Open'])


def verify_token(req: Request):
    token = req.headers["Authorization"]
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return token.split(' ')[1]


# 创建一个聊天记录
@router.post('/chat_message')
async def create_open_gpt_chat_message(
        chat_message_input: OpenGptChatMessageIn,
        open_gpt_key: str = Depends(verify_token),
):
    # 验证key
    key_info = await OpenGptKey.get_or_none(key=open_gpt_key, deleted_at__isnull=True)
    if key_info is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    new_obj = await OpenGptChatMessage.create(open_gpt_key_id=key_info.id, model=chat_message_input.model,
                                              messages=chat_message_input.messages)

    # 发送sse请求数据
    start_time = int(time.time())

    async def send_gpt():
        message = ''
        message_log = []
        new_msg_obj_id = new_obj.id
        for con in chat_message_input.messages:
            message_log.append({'role': con['role'], 'content': con['content']})
        agen = ask_open(key_info.gpt_key, message_log, chat_message_input.model, new_obj.id)
        async for event in agen:
            event_data = json.loads(event['data'])
            if event_data['sta'] == 'run':
                message = message + event_data['content']
                event['data'] = json.dumps(event_data)
                yield event
            else:
                end_time = int(time.time())
                await OpenGptChatMessage.filter(id=new_msg_obj_id).update(req_message=message,
                                                                          run_time=end_time - start_time)
                yield event
                await agen.aclose()

    return EventSourceResponse(send_gpt())


# 创建open gpt key
@router.post('/gpt_key', response_model=OpenGptKeyOut, )
async def create_open_gpt_key(
        gpt_key_input: OpenGptKeyIn, user: Auth0User = Security(auth.get_user)):
    # 创建一个sk秘钥
    sk = uuid.uuid4().hex
    new_obj = await OpenGptKey.create(key=sk, gpt_key=gpt_key_input.gpt_key, name=gpt_key_input.name)
    return new_obj
