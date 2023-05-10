import uuid

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi_auth0 import Auth0User

from teamgpt import settings
from teamgpt.models import MidjourneyProxyHook, MidjourneyProxySubmit, User
from teamgpt.schemata import MidjourneyProxySubmitIn, MidjourneyProxyHookToIn, MidjourneyProxySubmitUvIn
from teamgpt.settings import auth
from teamgpt.util.midjourney_proxy import url_submit, url_submit_uv

router = APIRouter(prefix='/api/v1/midjourney_proxy', tags=['MidjourneyProxy'])


# 提交任务
@router.post('/submit', response_model=None, dependencies=[Depends(auth.implicit_scheme)])
async def submit(mid_input: MidjourneyProxySubmitIn, user: Auth0User = Security(auth.get_user)):
    mid_input.notifyHook = settings.MIDJOURNEY_HOOK
    mid_input.state = str(uuid.uuid4())
    mid_input.taskId = mid_input.state
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    submit_obj = await MidjourneyProxySubmit.create(**mid_input.dict(exclude_unset=True), user=user_info)
    if submit_obj is not None:
        req_info = await url_submit(mid_input)
        if req_info['status_code'] == 200:
            await MidjourneyProxySubmit.filter(id=submit_obj.id).update(
                req_code=req_info['response_body']['code'],
                req_description=req_info['response_body']['description'],
                req_result=req_info['response_body']['result'],
            )
        return req_info
    else:
        raise HTTPException(status_code=400, detail="submit_obj is None")


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
    submit_info = await MidjourneyProxySubmit.filter(state=mid_input.state).first()
    if submit_info is not None:
        await MidjourneyProxySubmit.filter(id=submit_info.id).update(
            finish_time=mid_input.finishTime,
            image_url=mid_input.imageUrl,
            status=mid_input.status
        )
    return new_obj
