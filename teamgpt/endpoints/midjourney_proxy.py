from fastapi import APIRouter

from teamgpt import settings
from teamgpt.models import MidjourneyProxyHook
from teamgpt.schemata import MidjourneyProxyHookIn, MidjourneyProxySubmitIn, MidjourneyProxyHookToIn
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
    new_obj = await MidjourneyProxyHook.create(run_id=mid_input.id,
                                               action=mid_input.action,
                                               prompt=mid_input.prompt,
                                               promptEn=mid_input.promptEn,
                                               description=mid_input.description,
                                               state=mid_input.state,
                                               submitTime=mid_input.submitTime,
                                               finishTime=mid_input.finishTime,
                                               imageUrl=mid_input.imageUrl,
                                               status=mid_input.status)
    return new_obj
