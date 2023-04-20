import json
from typing import Optional

from fastapi import APIRouter, Depends, Security, HTTPException
from starlette.status import HTTP_204_NO_CONTENT
from stripe.http_client import requests

from teamgpt.models import GptTopic, GptPrompt, User
from teamgpt.parameters import Page, tortoise_paginate, ListAPIParams
from teamgpt.schemata import GptTopicOut, GptTopicIn, GptPromptIn, GptPromptOut, GptPromptToOut

from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User

router = APIRouter(prefix='/api/v1/gpt_prompt', tags=['GptPrompt'])


# 增加一个GptTopic
@router.post(
    '/gpt_topic',
    response_model=GptTopicOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_gpt_topic(
        gpt_topic_input: GptTopicIn,
        organization_id: Optional[str] = None,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    new_gpt_topic_obj = await GptTopic.create(title=gpt_topic_input.title, description=gpt_topic_input.description,
                                              pid=gpt_topic_input.pid, organization_id=organization_id, user=user_info)
    return await GptTopicOut.from_tortoise_orm(new_gpt_topic_obj)


# 获取所有的GptTopic
@router.get(
    '/gpt_topics',
    response_model=Page[GptTopicOut],
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_gpt_topics(
        user: Auth0User = Security(auth.get_user),
        pid: Optional[str] = None,
        organization_id: Optional[str] = None,
        params: ListAPIParams = Depends()
):
    query_params = {'deleted_at__isnull': True}
    if organization_id is not None:
        query_params['organization_id'] = organization_id
    if pid is not None:
        query_params['pid'] = pid
    else:
        query_params['pid__isnull'] = True
    gpt_topics = GptTopic.filter(**query_params)
    return await tortoise_paginate(gpt_topics, params)


# 查询所有gptTopic
@router.get(
    '/gpt_topic_all',
    response_model=list[GptTopicOut],
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_gpt_topic_all(
        user: Auth0User = Security(auth.get_user),
        organization_id: Optional[str] = None,
):
    query_params = {'deleted_at__isnull': True}
    if organization_id is not None:
        query_params['organization_id'] = organization_id
    gpt_topics = await GptTopic.filter(**query_params).all()
    return gpt_topics


# 删除一个GptTopic
@router.delete(
    '/gpt_topic/{gpt_topic_id}',
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def delete_gpt_topic(
        gpt_topic_id: str,
        user: Auth0User = Security(auth.get_user)
):
    gpt_obj = await GptTopic.get_or_none(id=gpt_topic_id, deleted_at__isnull=True)
    if gpt_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await gpt_obj.soft_delete()


# 修改一个GptTopic
@router.put(
    '/gpt_topic/{gpt_topic_id}',
    response_model=GptTopicOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def update_gpt_topic(
        gpt_topic_id: str,
        gpt_topic_input: GptTopicIn,
        user: Auth0User = Security(auth.get_user)
):
    gpt_obj = await GptTopic.get_or_none(id=gpt_topic_id, deleted_at__isnull=True)
    if gpt_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await gpt_obj.update_from_dict(gpt_topic_input.dict(exclude_unset=True)).save()
    return await GptTopicOut.from_tortoise_orm(gpt_obj)


# 新增一个GptPrompt
@router.post(
    '',
    response_model=GptPromptOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_gpt_prompt(
        gpt_prompt_input: GptPromptIn,
        organization_id: Optional[str] = None,
        gpt_topic_id: Optional[str] = None,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    new_gpt_prompt_obj = await GptPrompt.create(belong=gpt_prompt_input.belong,
                                                prompt_template=gpt_prompt_input.prompt_template,
                                                prompt_hint=gpt_prompt_input.prompt_hint,
                                                teaser=gpt_prompt_input.teaser,
                                                title=gpt_prompt_input.title,
                                                organization_id=organization_id,
                                                gpt_topic_id=gpt_topic_id,
                                                user=user_info
                                                )
    return await GptPromptOut.from_tortoise_orm(new_gpt_prompt_obj)


# 删除一个GptPrompt
@router.delete(
    '/{gpt_prompt_id}',
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def delete_gpt_prompt(
        gpt_prompt_id: str,
        user: Auth0User = Security(auth.get_user)
):
    gpt_obj = await GptPrompt.get_or_none(id=gpt_prompt_id, deleted_at__isnull=True)
    if gpt_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await gpt_obj.soft_delete()


# 修改一个GptPrompt
@router.put(
    '/{gpt_prompt_id}',
    response_model=GptPromptOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def update_gpt_prompt(
        gpt_prompt_id: str,
        gpt_prompt_input: GptPromptIn,
        user: Auth0User = Security(auth.get_user)
):
    gpt_obj = await GptPrompt.get_or_none(id=gpt_prompt_id, deleted_at__isnull=True)
    if gpt_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await gpt_obj.update_from_dict(gpt_prompt_input.dict(exclude_unset=True)).save()
    return await GptPromptOut.from_tortoise_orm(gpt_obj)


# 查询GptPrompt
@router.get(
    '',
    response_model=Page[GptPromptToOut],
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_gpt_prompts(
        user: Auth0User = Security(auth.get_user),
        organization_id: Optional[str] = None,
        gpt_topic_id: Optional[str] = None,
        belong: Optional[str] = None,
        params: ListAPIParams = Depends()
):
    query_params = {'deleted_at__isnull': True}
    if organization_id is not None:
        query_params['organization_id'] = organization_id
    if gpt_topic_id is not None:
        gpt_topic_info = await GptTopic.get_or_none(id=gpt_topic_id, deleted_at__isnull=True)
        if gpt_topic_info.pid is not None:
            query_params['gpt_topic_id'] = gpt_topic_id
        else:
            gpt_topic_pid_list = await GptTopic.filter(pid=gpt_topic_id, deleted_at__isnull=True).values_list('id',
                                                                                                              flat=True)
            query_params['gpt_topic_id__in'] = gpt_topic_pid_list

    if belong is not None:
        belong_list = belong.split(',')
        gpt_prompts = GptPrompt.filter(**query_params).filter(belong__contains=belong_list)
    else:
        gpt_prompts = GptPrompt.filter(**query_params)
    return await tortoise_paginate(gpt_prompts, params, ['user'])


@router.get("/test/")
async def test(org_id: str, gpt_topic_id: str):
    url = 'https://api.aiprm.com/api3/Prompts?Community=SEO-84c5d6a7b8e9f0c1&Limit=10&Offset=0&OwnerExternalID=user-Nq8Ozuosjlt0cbWcesw4FxAz&OwnerExternalSystemNo=1&SortModeNo=2&UserFootprint='
    response = requests.get(url)
    data_list = response.json()
    for data in data_list:
        await GptPrompt.create(
            belong=['public'],
            title=data['Title'],
            prompt_hint=data['PromptHint'],
            organization_id=org_id,
            gpt_topic_id=gpt_topic_id,
            teaser=data['Teaser'],
            prompt_template=data['Prompt'],
        )
