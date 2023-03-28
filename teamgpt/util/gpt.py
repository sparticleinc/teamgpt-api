import openai


async def get_events():
    openai.api_key = "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"
    message_log = [
        {"content": "Hello, I am a chat robot.", "role": "system"},
        {"content": "宁波有几条地铁", "role": "user"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 使用 gpt-3.5-turbo 模型
        messages=message_log,
        stream=True
    )
    for chunk in response:
        if 'content' in chunk['choices'][0]['delta']:
            data = chunk['choices'][0]['delta']['content']
        else:
            data = ''
        yield {
            "event": "text",
            "data": data,
        }
