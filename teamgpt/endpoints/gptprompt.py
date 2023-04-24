import csv
from typing import Optional

import requests
from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi_auth0 import Auth0User
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.models import GptTopic, GptPrompt, User
from teamgpt.parameters import Page, tortoise_paginate, ListAPIParams
from teamgpt.schemata import GptTopicOut, GptTopicIn, GptPromptIn, GptPromptOut, GptPromptToOut
from teamgpt.settings import (auth)

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


# 同步https://app1.aiprm.com/的prompt
@router.get("/sync/aiprm", dependencies=[Depends(auth.implicit_scheme)])
async def sync_aiprm():
    # 取出所有的topic,插入表
    topic_url = 'https://api.aiprm.com/csv/topics-20230123.csv'
    topic_response = requests.get(topic_url)
    topic_reader = csv.reader(topic_response.text.strip().split('\n'))
    next(topic_reader)
    for row in topic_reader:
        await GptTopic.get_or_create(title=row[1], pid=None, organization_id=None, user_id=None,
                                     deleted_at__isnull=True, )
    # 取出所有activities,插入表
    activities_url = 'https://api.aiprm.com/csv/activities-20230124.csv'
    activities_response = requests.get(activities_url)
    activities_reader = csv.reader(activities_response.text.strip().split('\n'))
    next(activities_reader)
    for row in activities_reader:
        index = row[0].index('-')
        new_text = row[0][:index]
        if new_text != '':
            if new_text == 'OperatingSystems':
                new_text = 'Operating Systems'
            if new_text == 'Applications':
                new_text = 'Software Applications'
            if new_text == 'SoftwareEngineering':
                new_text = 'Software Engineering'
            if new_text == 'Generative':
                new_text = 'Generative AI'
        if new_text != '':
            pid_info = await GptTopic.get_or_none(title=new_text, pid=None, organization_id=None, user_id=None,
                                                  deleted_at__isnull=True)
            if pid_info is not None:
                await GptTopic.get_or_create(title=row[1], pid=pid_info.id, organization_id=None, user_id=None,
                                             deleted_at__isnull=True, )
    # 取出prompt，插入表
    url = 'https://api.aiprm.com/api3/Prompts?Community=&Limit=999999&Offset=0&OwnerExternalID=user-Nq8Ozuosjlt0cbWcesw4FxAz&OwnerExternalSystemNo=1'
    response = requests.get(url)
    i = 0
    data_list = response.json()
    for data in data_list:
        community_index = data['Community'].index('-')
        new_text = data['Community'][:community_index]
        if new_text != '':
            if new_text == 'OperatingSystems':
                new_text = 'Operating Systems'
            if new_text == 'Applications':
                new_text = 'Software Applications'
            if new_text == 'SoftwareEngineering':
                new_text = 'Software Engineering'
            if new_text == 'Generative':
                new_text = 'Generative AI'
            community_topic_info = await GptTopic.get_or_none(title=new_text, pid=None,
                                                              organization_id=None, user_id=None,
                                                              deleted_at__isnull=True)
            if community_topic_info is not None:
                i = i + 1
                topic_info = await GptTopic.get_or_none(pid=community_topic_info.id, title=data['Category'],
                                                        organization_id=None,
                                                        user_id=None,
                                                        deleted_at__isnull=True)
                if topic_info is not None:
                    gpt_topic_id = topic_info.id
                    gpt_prompt = await GptPrompt.filter(title=data['Title'], gpt_topic_id=gpt_topic_id).first()
                    if gpt_prompt is not None:
                        gpt_prompt.prompt_hint = data['PromptHint']
                        gpt_prompt.teaser = data['Teaser']
                        gpt_prompt.prompt_template = data['Prompt']
                        await gpt_prompt.save()
                    else:
                        await GptPrompt.create(
                            belong=['public'],
                            title=data['Title'],
                            prompt_hint=data['PromptHint'],
                            gpt_topic_id=gpt_topic_id,
                            teaser=data['Teaser'],
                            prompt_template=data['Prompt'],
                        )
    return {'msg': 'success', 'count': i}
