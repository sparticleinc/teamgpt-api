import uuid

from fastapi import APIRouter

from teamgpt.models import MidjourneyProxyHook
from teamgpt.schemata import MidjourneyProxySubmitIn, MidjourneyProxyHookToIn
from teamgpt.util.midjourney_proxy import url_submit

router = APIRouter(prefix='/api/v1/midjourney_proxy', tags=['MidjourneyProxy'])


# 测试通过接口发出任务
@router.post('/submit', response_model=None)
async def submit(mid_input: MidjourneyProxySubmitIn):
    req_info = await url_submit(mid_input)
    return req_info


# hook回调
@router.post('/hook')
async def hook(mid_input: MidjourneyProxyHookToIn):
    run_id = mid_input.id
    mid_input.id = uuid.uuid4()
    new_obj = await MidjourneyProxyHook.create(**mid_input.dict(), run_id=run_id)
    return new_obj
