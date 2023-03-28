import openai

from teamgpt.settings import (GPT_KEY)


async def get_events():
    openai.api_key = GPT_KEY
    message_log = [
        {"content": "Hello, I am a chat robot.", "role": "system"},
        {"content": "you name", "role": "user"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_log,
        stream=True
    )
    for chunk in response:
        if 'content' in chunk['choices'][0]['delta']:
            message = chunk['choices'][0]['delta']['content']
        else:
            message = ''
        yield {
            "event": "text",
            "data": {'message': message, 'sta': chunk['choices'][0]['finish_reason']},
        }


async def ask(api_key: str, message_log: list, model: str, conversations_id: str):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=message_log,
        stream=True
    )
    for chunk_msg in response:
        if 'content' in chunk_msg['choices'][0]['delta']:
            message = chunk_msg['choices'][0]['delta']['content']
        else:
            message = ''
        yield {
            "event": "text",
            "data": {'message': message, 'sta': chunk_msg['choices'][0]['finish_reason'], 'id': conversations_id},
        }
