import json
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette import EventSourceResponse

from teamgpt.models import OpenGptKey, OpenGptChatMessage
from teamgpt.schemata import OpenGptKeyIn, OpenGptKeyOut, OpenGptChatMessageIn
from teamgpt.util.gpt import ask_open, ask_open_v2, num_tokens_from_messages, msg_tiktoken_num

router = APIRouter(prefix='/v1', tags=['V1'])


def verify_token(req: Request):
    token = req.headers["Authorization"]
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return token.split(' ')[1]


@router.post('/chat/completions')
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
    if chat_message_input.functions is not None:
        new_obj = await OpenGptChatMessage.create(open_gpt_key_id=key_info.id, model=chat_message_input.model,
                                                  messages=chat_message_input.messages,
                                                  functools=chat_message_input.functions)
    else:
        new_obj = await OpenGptChatMessage.create(open_gpt_key_id=key_info.id, model=chat_message_input.model,
                                                  messages=chat_message_input.messages)
    if chat_message_input.stream is None or chat_message_input.stream is False:
        message_log = []
        new_msg_obj_id = new_obj.id
        for con in chat_message_input.messages:
            message_log.append({'role': con['role'], 'content': con['content']})
        agen = await ask_open_v2(key_info.gpt_key, chat_message_input)
        await OpenGptChatMessage.filter(id=new_msg_obj_id).update(req_message=agen,
                                                                  prompt_tokens=agen.usage['prompt_tokens'],
                                                                  completion_tokens=agen.usage['completion_tokens'],
                                                                  total_tokens=agen.usage['total_tokens']
                                                                  )
        return agen
    else:
        # 发送sse请求数据
        start_time = int(time.time())

        async def send_gpt():
            message = ''
            message_log = []
            new_msg_obj_id = new_obj.id
            for con in chat_message_input.messages:
                message_log.append({'role': con['role'], 'content': con['content']})
            agen = ask_open(key_info.gpt_key, message_log, chat_message_input.model)
            async for event in agen:
                event_data = event['data']
                loads_json = json.loads(event_data)
                if 'content' in loads_json['choices'][0]['delta']:
                    message = message + loads_json['choices'][0]['delta']['content']
                yield event
                if loads_json['choices'][0]['finish_reason'] == 'stop':
                    yield {
                        'data': '[DONE]'
                    }
                    end_time = int(time.time())
                    prompt_tokens = await num_tokens_from_messages(message_log[::-1], model=chat_message_input.model)
                    req_token_num = await msg_tiktoken_num(message, model=chat_message_input.model)
                    total_tokens = prompt_tokens + req_token_num
                    await OpenGptChatMessage.filter(id=new_msg_obj_id).update(req_message=message,
                                                                              completion_tokens=req_token_num,
                                                                              prompt_tokens=prompt_tokens,
                                                                              total_tokens=total_tokens,
                                                                              run_time=end_time - start_time)
                    await agen.aclose()

        return EventSourceResponse(send_gpt(), headers={'content-type': 'text/event-stream', 'charset': 'utf-8'})


# 创建open gpt key
@router.post('/gpt_key', response_model=OpenGptKeyOut, )
async def create_open_gpt_key(
        gpt_key_input: OpenGptKeyIn):
    # 创建一个sk秘钥
    sk = uuid.uuid4().hex
    new_obj = await OpenGptKey.create(key=sk, gpt_key=gpt_key_input.gpt_key, name=gpt_key_input.name)
    return new_obj
