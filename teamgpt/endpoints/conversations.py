import json
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi_pagination import Page
from sse_starlette import EventSourceResponse
from starlette.status import HTTP_204_NO_CONTENT
from typing import Union

from teamgpt.enums import GptModel, ContentType, AutherUser, GptKeySource
from teamgpt.models import User, Conversations, ConversationsMessage, GPTKey, Organization, SysGPTKey, GptChatMessage
from teamgpt.schemata import ConversationsIn, ConversationsOut, ConversationsMessageIn, ConversationsMessageOut
from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User
from teamgpt.parameters import ListAPIParams, tortoise_paginate
from teamgpt.util.gpt import get_events, ask

router = APIRouter(prefix='/conversations', tags=['Conversations'])


@router.get('/sse-demo')
async def sse_conversations_message(
):
    async def event_generator():
        message = ''
        agen = get_events()
        async for event in agen:
            event_data = json.loads(event['data'])
            if event_data['sta'] == 'run':
                message = message + event_data['message']
                yield event
            else:
                yield event
                await agen.aclose()

    return EventSourceResponse(event_generator())


# create conversations
@router.post('/{organization_id}', response_model=ConversationsOut, dependencies=[Depends(auth.implicit_scheme)])
async def create_conversations(
        conversations_input: ConversationsIn,
        organization_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    new_obj = await Conversations.create(user=user_info, title=conversations_input.title,
                                         organization_id=organization_id)
    return await ConversationsOut.from_tortoise_orm(new_obj)


# del conversations
@router.delete('/{organization_id}/{conversations_id}', status_code=HTTP_204_NO_CONTENT,
               dependencies=[Depends(auth.implicit_scheme)])
async def del_conversations(
        organization_id: str,
        conversations_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    con_obj = await Conversations.get_or_none(id=conversations_id, organization_id=organization_id, user=user_info,
                                              deleted_at__isnull=True)
    if con_obj is None:
        raise HTTPException(status_code=404, detail='Conversation not found')
    await con_obj.soft_delete()


# edit conversations
@router.put('/{organization_id}/{conversations_id}', response_model=ConversationsOut,
            dependencies=[Depends(auth.implicit_scheme)])
async def edit_conversations(
        conversations_input: ConversationsIn,
        organization_id: str,
        conversations_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    con_obj = await Conversations.get_or_none(id=conversations_id, organization_id=organization_id, user=user_info,
                                              deleted_at__isnull=True)
    if con_obj is None:
        raise HTTPException(status_code=404, detail='Conversation not found')
    con_obj.title = conversations_input.title
    await con_obj.save()
    return await ConversationsOut.from_tortoise_orm(con_obj)


# get conversations
@router.get('/{organization_id}', response_model=Page[ConversationsOut], dependencies=[Depends(auth.implicit_scheme)])
async def get_conversations(
        organization_id: str,
        user: Auth0User = Security(auth.get_user),
        params: ListAPIParams = Depends()
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    con_org = Conversations.filter(user=user_info, organization_id=organization_id, deleted_at__isnull=True)
    return await tortoise_paginate(con_org, params)


# create conversations message
@router.post('/message/{organization_id}',
             dependencies=[Depends(auth.implicit_scheme)])
async def create_conversations_message(
        conversations_input_list: list[ConversationsMessageIn],
        organization_id: str,
        conversation_id: Union[str, None] = None,
        title: Union[str, None] = None,
        model: Union[GptModel, None] = Query(default=GptModel.GPT3TURBO),
        context_number: Union[int, None] = Query(default=10),
        user: Auth0User = Security(auth.get_user)
):
    # 查询gpt-key配置信息,判断是否是系统的
    key = ''
    org_info = await Organization.get_or_none(id=organization_id, deleted_at__isnull=True)
    if org_info is None:
        raise HTTPException(status_code=404, detail='Organization not found')
    if org_info.gpt_key_source is GptKeySource.SYSTEM:
        sys_gpt_key = await SysGPTKey.get_or_none(deleted_at__isnull=True)
        if sys_gpt_key is None:
            raise HTTPException(status_code=404, detail='SYS GPT key not found')
        key = sys_gpt_key.key
    else:
        gpt_key = await GPTKey.get_or_none(organization_id=organization_id, deleted_at__isnull=True)
        if gpt_key is None:
            raise HTTPException(status_code=404, detail='GPT key not found')
        key = gpt_key.key
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    message_log = []
    # 判断是否存在会话,没有先创建会话
    conversation_obj = await Conversations.get_or_none(id=conversation_id, deleted_at__isnull=True)
    if conversation_obj is None:
        if len(conversations_input_list) > 1:
            new_obj = await Conversations.create(id=uuid.UUID(conversation_id), user=user_info, title=title,
                                                 organization_id=organization_id,
                                                 model=model)
            conversation_id = new_obj.id
        else:
            raise HTTPException(status_code=400, detail='Conversation format error')
    else:
        con_obj = await Conversations.get_or_none(id=conversation_id, deleted_at__isnull=True)
        if con_obj is None:
            raise HTTPException(status_code=404, detail='Conversation not found')
        model = con_obj.model

    # 循环消息插入数据库
    for conversations_input in conversations_input_list:
        await ConversationsMessage.create(user=user_info, conversation_id=conversation_id,
                                          message=conversations_input.message,
                                          author_user=conversations_input.author_user,
                                          content_type=conversations_input.content_type,
                                          key=key,
                                          )
    # 查询前5条消息
    con_org = await ConversationsMessage.filter(user=user_info, conversation_id=conversation_id,
                                                deleted_at__isnull=True).order_by('-created_at').limit(context_number)
    for con in con_org:
        message_log.append({'role': con.author_user, 'content': con.message})
    # 发送sse请求数据
    start_time = int(time.time())

    async def send_gpt():
        message = ''
        new_msg_obj_id = ''
        agen = ask(key, message_log[::-1], model, conversation_id)
        async for event in agen:
            event_data = json.loads(event['data'])
            if event_data['sta'] == 'run':
                message = message + event_data['message']
                if new_msg_obj_id == '':
                    new_msg_obj = await ConversationsMessage.create(user=user_info, conversation_id=conversation_id,
                                                                    message=message,
                                                                    author_user=AutherUser.ASSISTANT,
                                                                    content_type=ContentType.TEXT,
                                                                    key=key,
                                                                    )
                    new_msg_obj_id = str(new_msg_obj.id)
                event_data['msg_id'] = new_msg_obj_id
                event['data'] = json.dumps(event_data)
                yield event
            else:
                end_time = int(time.time())
                await ConversationsMessage.filter(id=new_msg_obj_id).update(message=message,
                                                                            run_time=end_time - start_time)
                await GptChatMessage.create(in_message=json.dumps(message_log, ensure_ascii=False), out_message=message,
                                            key=key,
                                            user=user_info,
                                            organization_id=org_info.id, conversation_id=conversation_id, )
                yield event
                await agen.aclose()

    return EventSourceResponse(send_gpt())


# get conversations message
@router.get('/message/{conversations_id}',
            response_model=Page[ConversationsMessageOut], dependencies=[Depends(auth.implicit_scheme)])
async def get_conversations_message(
        conversations_id: str,
        user: Auth0User = Security(auth.get_user),
        params: ListAPIParams = Depends()
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    con_org = ConversationsMessage.filter(user=user_info, conversation_id=conversations_id,
                                          deleted_at__isnull=True)
    return await tortoise_paginate(con_org, params)
