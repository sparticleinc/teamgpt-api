import json

import openai


async def ask(api_key: str, message_log: list, model: str, conversations_id: str):
    openai.api_key = api_key
    try:
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
