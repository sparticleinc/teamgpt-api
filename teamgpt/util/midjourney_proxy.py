import requests

from teamgpt import settings
from teamgpt.schemata import MidjourneyProxySubmitIn


async def url_submit(payload: MidjourneyProxySubmitIn):
    url = settings.MIDJOURNEY_PROXY_URL + '/mj/trigger/submit'
    headers = {"Content-Type": "application/json"}
    print(settings.MIDJOURNEY_HOOK, '2323')
    response = requests.post(url, json={
        "action": payload.action,
        "prompt": payload.prompt,
        "taskId": payload.taskId,
        "index": payload.index,
        "state": payload.state,
        "notifyHook": settings.MIDJOURNEY_HOOK
    }, headers=headers)
    return {"status_code": response.status_code, "response_body": response.json()}
