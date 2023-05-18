import json

import openai
import tiktoken

from teamgpt.models import OpenGptChatMessage


async def ask(api_key: str, message_log: list, model: str, conversations_id: str):
    openai.api_key = api_key
    try:
        async for chunk_msg in await openai.ChatCompletion.acreate(
                model=model,
                messages=message_log,
                stream=True
        ):
            # completion_tokens = await num_tokens_from_messages(chunk_msg, model=model)
            if 'content' in chunk_msg['choices'][0]['delta']:
                message = chunk_msg['choices'][0]['delta']['content']
            else:
                message = ''
            sta = 'run'
            if chunk_msg['choices'][0]['finish_reason'] == 'stop' or chunk_msg['choices'][0][
                'finish_reason'] == 'length':
                sta = 'stop'
            yield {
                "data": json.dumps(
                    {'message': message, 'sta': sta, 'conversation_id': str(conversations_id), 'msg_id': ''}),
            }
    except Exception as e:
        yield {
            "data": json.dumps({'error': str(e), 'sta': 'error'}),
        }


async def ask_open(api_key: str, message_log: list, model: str):
    openai.api_key = api_key
    try:
        async for chunk_msg in await openai.ChatCompletion.acreate(
                model=model,
                messages=message_log,
                stream=True
        ):
            yield {
                "data": json.dumps(chunk_msg),
            }
    except Exception as e:
        yield {
            "data": json.dumps(e),
        }


async def ask_open_v2(api_key: str, chat_message_input: OpenGptChatMessage):
    openai.api_key = api_key
    ret = await openai.ChatCompletion.acreate(
        **chat_message_input.dict(exclude_unset=True)
    )
    return ret


async def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError()
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


async def msg_tiktoken_num(messages, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    num_tokens += len(encoding.encode(messages))
    return num_tokens
