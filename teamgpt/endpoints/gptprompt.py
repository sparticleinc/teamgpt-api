from typing import Optional

from fastapi import APIRouter, Depends, Security, HTTPException
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.models import GptTopic, GptPrompt
from teamgpt.parameters import Page, tortoise_paginate, ListAPIParams
from teamgpt.schemata import GptTopicOut, GptTopicIn, GptPromptIn, GptPromptOut

from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User

router = APIRouter(prefix='/gpt_prompt', tags=['GptPrompt'])


# 增加一个GptTopic
@router.post(
    '/gpt_topic',
    response_model=GptTopicOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_gpt_topic(
        gpt_topic_input: GptTopicIn,
        user: Auth0User = Security(auth.get_user)
):
    new_gpt_topic_obj = await GptTopic.create(**gpt_topic_input.dict(exclude_unset=True))
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
        params: ListAPIParams = Depends()
):
    query_params = {'deleted_at__isnull': True}
    if pid is not None:
        query_params['pid'] = pid
    else:
        query_params['pid__isnull'] = True
    gpt_topics = GptTopic.filter(**query_params)
    return await tortoise_paginate(gpt_topics, params)


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
    '/',
    response_model=GptPromptOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_gpt_prompt(
        gpt_prompt_input: GptPromptIn,
        organization_id: Optional[str] = None,
        gpt_topic_id: Optional[str] = None,
        user: Auth0User = Security(auth.get_user)
):
    new_gpt_prompt_obj = await GptPrompt.create(belong=gpt_prompt_input.belong,
                                                prompt_template=gpt_prompt_input.prompt_template,
                                                prompt_hint=gpt_prompt_input.prompt_hint,
                                                teaser=gpt_prompt_input.teaser,
                                                title=gpt_prompt_input.title,
                                                organization_id=organization_id,
                                                gpt_topic_id=gpt_topic_id,
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
    '/',
    response_model=Page[GptPromptOut],
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
        query_params['gpt_topic_id'] = gpt_topic_id
    if belong is not None:
        query_params['belong'] = belong
    gpt_prompts = GptPrompt.filter(**query_params)
    return await tortoise_paginate(gpt_prompts, params)
