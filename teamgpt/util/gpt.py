import openai

from teamgpt.settings import (GPT_KEY)


async def get_events():
    openai.api_key = GPT_KEY
    message_log = [
        {"content": "Hello, I am a chat robot.", "role": "system"},
        {"content": "you name", "role": "user"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 使用 gpt-3.5-turbo 模型
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
