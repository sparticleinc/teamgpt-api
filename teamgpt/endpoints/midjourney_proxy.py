import uuid

from fastapi import APIRouter

from teamgpt.models import MidjourneyProxyHook
from teamgpt.schemata import MidjourneyProxySubmitIn, MidjourneyProxyHookToIn, MidjourneyProxySubmitUvIn
from teamgpt.util.midjourney_proxy import url_submit, url_submit_uv

router = APIRouter(prefix='/api/v1/midjourney_proxy', tags=['MidjourneyProxy'])


# 提交任务
@router.post('/submit', response_model=None)
async def submit(mid_input: MidjourneyProxySubmitIn):
    req_info = await url_submit(mid_input)
    return req_info


# 提交选中放大或变换任务
@router.post("submit_uv", response_model=None)
async def submit_uv(mid_input: MidjourneyProxySubmitUvIn):
    req_info = await url_submit_uv(mid_input)
    return req_info


# hook回调
@router.post('/hook')
async def hook(mid_input: MidjourneyProxyHookToIn):
    run_id = mid_input.id
    mid_input.id = uuid.uuid4()
    new_obj = await MidjourneyProxyHook.create(**mid_input.dict(), run_id=run_id)
    return new_obj
