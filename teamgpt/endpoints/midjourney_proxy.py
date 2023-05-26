import datetime
import json
import time
import uuid

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi_auth0 import Auth0User

from teamgpt import settings
from teamgpt.endpoints.stripe import org_payment_plan
from teamgpt.models import MidjourneyProxyHook, MidjourneyProxySubmit, User, Organization
from teamgpt.parameters import ListAPIParams, tortoise_paginate
from teamgpt.schemata import MidjourneyProxySubmitIn, MidjourneyProxyHookToIn, SendWsData
from teamgpt.settings import auth
from teamgpt.util.midjourney_proxy import url_submit, url_task_fetch
from teamgpt.util.ws import manager

router = APIRouter(prefix='/api/v1/midjourney_proxy', tags=['MidjourneyProxy'])


# 查询个人的提交记录列表
@router.get('/submit_list', dependencies=[Depends(auth.implicit_scheme)])
async def get_submit_list(user: Auth0User = Security(auth.get_user), params: ListAPIParams = Depends()):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    submit_obj = MidjourneyProxySubmit.filter(user=user_info, deleted_at__isnull=True)
    return await tortoise_paginate(submit_obj, params, ['user'])


# 提交任务
@router.post('/submit', dependencies=[Depends(auth.implicit_scheme)])
async def submit(mid_input: MidjourneyProxySubmitIn, user: Auth0User = Security(auth.get_user)):
    # 查看当前组织是否在试用期,试用期只能生成一张图片
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    org = await Organization.get_or_none(id=user_info.current_organization, deleted_at__isnull=True)
    if org is None:
        raise HTTPException(status_code=400, detail="The current user has no organization.")
    if user_info.current_organization is None or user_info.current_organization is '':
        raise HTTPException(status_code=400, detail="The current user has no organization.")
    count_day_submit = await MidjourneyProxySubmit.filter(user=user_info,
                                                          organization=org,
                                                          created_at__gte=datetime.datetime.now() - datetime.
                                                          timedelta(days=1)).count()
    if count_day_submit >= 1:
        plan_info = await org_payment_plan(org)
        if plan_info.is_super is False:
            if plan_info.is_plan is False:
                raise HTTPException(status_code=424, detail="")
    mid_input.notifyHook = settings.MIDJOURNEY_HOOK
    mid_input.state = str(uuid.uuid4())
    if mid_input.action != 'IMAGINE':
        mid_info = await MidjourneyProxySubmit.filter(taskId=mid_input.taskId).first()
        if mid_info is not None:
            mid_input.taskId = mid_info.req_result
    else:
        mid_input.taskId = mid_input.state
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    submit_obj = await MidjourneyProxySubmit.create(**mid_input.dict(exclude_unset=True), user=user_info,
                                                    organization=org)
    if submit_obj is not None:
        req_info = await url_submit(mid_input)
        if req_info['status_code'] == 200:
            await MidjourneyProxySubmit.filter(id=submit_obj.id).update(
                req_code=req_info['response_body']['code'],
                req_description=req_info['response_body']['description'],
                req_result=req_info['response_body']['result'],
            )
        req_info['info'] = submit_obj
        return req_info
    else:
        raise HTTPException(status_code=400, detail="submit_obj is None")


# 查询单个任务
@router.get('/submit/{id}')
async def get_submit(task_id: str):
    req_info = await url_task_fetch(task_id)
    return req_info


# hook回调
@router.post('/hook')
async def hook(mid_input: MidjourneyProxyHookToIn):
    run_id = mid_input.id
    mid_input.id = uuid.uuid4()
    new_obj = await MidjourneyProxyHook.create(**mid_input.dict(), run_id=run_id)
    submit_info = await MidjourneyProxySubmit.filter(state=mid_input.state).prefetch_related('user').first()
    await manager.broadcast(json.dumps(SendWsData(
        type='midjourney_hook',
        client_id=submit_info.user.user_id,
        timestamp=int(time.time()),
        data={
            'finish_time': mid_input.finishTime,
            'image_url': mid_input.imageUrl,
            'status': mid_input.status,
            'taskId': submit_info.taskId,
            'id': str(submit_info.id)
        }
    ).dict()), 'midjourney:' + str(submit_info.user.user_id))
    if submit_info is not None:
        await MidjourneyProxySubmit.filter(id=submit_info.id).update(
            finish_time=mid_input.finishTime,
            image_url=mid_input.imageUrl,
            status=mid_input.status
        )
    return new_obj
