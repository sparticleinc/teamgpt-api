from fastapi import APIRouter

from teamgpt.models import MidjourneyProxyHook
from teamgpt.schemata import MidjourneyProxyHookIn

router = APIRouter(prefix='/api/v1/midjourney_proxy', tags=['MidjourneyProxy'])


# 测试通过接口发出任务


# hook回调
@router.post('/hook')
async def hook(mid_input: MidjourneyProxyHookIn):
    await MidjourneyProxyHook.create(**mid_input.dict())
    return {'status': 'ok'}
