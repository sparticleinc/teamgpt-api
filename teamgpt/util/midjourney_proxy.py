import requests

from teamgpt import settings
from teamgpt.schemata import MidjourneyProxySubmitIn, MidjourneyProxySubmitUvIn


async def url_submit(payload: MidjourneyProxySubmitIn):
    url = settings.MIDJOURNEY_PROXY_URL + '/mj/trigger/submit'
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={
        "action": payload.action,
        "prompt": payload.prompt,
        "taskId": payload.taskId,
        "index": payload.index,
        "state": payload.state,
        "notifyHook": payload.notifyHook
    }, headers=headers)
    return {"status_code": response.status_code, "response_body": response.json()}


async def url_submit_uv(payload: MidjourneyProxySubmitUvIn):
    url = settings.MIDJOURNEY_PROXY_URL + '/mj/trigger/submit-uv'
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={
        'content': payload.content,
        "state": payload.state,
        "notifyHook": settings.MIDJOURNEY_HOOK
    }, headers=headers)
    return {"status_code": response.status_code, "response_body": response.json()}


async def url_task_fetch(task_id: str):
    url = settings.MIDJOURNEY_PROXY_URL + '/mj/task/' + task_id + '/fetch'
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return {"status_code": response.status_code, "response_body": response.json()}
