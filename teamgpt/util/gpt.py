import json

import openai
import tiktoken

from teamgpt.models import OpenGptChatMessage
from teamgpt.schemata import OpenGptChatMessageIn


async def ask(api_key: str, message_log: list, model: str, conversations_id: str):
    openai.api_key = api_key
    try:
        async for chunk_msg in await openai.ChatCompletion.acreate(
                model=model,
                messages=message_log,
                stream=True
        ):
            if 'content' in chunk_msg['choices'][0]['delta']:
                message = chunk_msg['choices'][0]['delta']['content']
            else:
                message = ''
            sta = 'run'
            if chunk_msg['choices'][0]['finish_reason'] == 'stop':
                sta = 'stop'
            yield {
                "data": json.dumps(
                    {'message': message, 'sta': sta, 'conversation_id': str(conversations_id), 'msg_id': ''}),
            }
    except Exception as e:
        yield {
            "data": json.dumps({'error': str(e), 'sta': 'error'}),
        }


async def ask_open(api_key: str, message_log: list, model: str, conversations_id: str):
    openai.api_key = api_key
    try:
        async for chunk_msg in await openai.ChatCompletion.acreate(
                model=model,
                messages=message_log,
                stream=True
        ):
            if 'content' in chunk_msg['choices'][0]['delta']:
                message = chunk_msg['choices'][0]['delta']['content']
            else:
                message = ''
            sta = 'run'
            if chunk_msg['choices'][0]['finish_reason'] == 'stop':
                sta = 'stop'
            yield {
                "data": json.dumps(
                    {'content': message, 'sta': sta}),
            }
    except Exception as e:
        yield {
            "data": json.dumps({'error': str(e), 'sta': 'error'}),
        }


async def ask_open_v2(api_key: str, chat_message_input: OpenGptChatMessage):
    openai.api_key = api_key
    ret = await openai.ChatCompletion.acreate(
        **chat_message_input.dict(exclude_unset=True)
    )
    return ret


async def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
