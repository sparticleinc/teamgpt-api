import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Union

import openai
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi_auth0 import Auth0User
from fastapi_pagination import Page
from sse_starlette import EventSourceResponse
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.endpoints.stripe import org_payment_plan
from teamgpt.enums import GptModel, ContentType, AutherUser, GptKeySource
from teamgpt.models import User, Conversations, ConversationsMessage, GPTKey, Organization, SysGPTKey, GptChatMessage
from teamgpt.parameters import ListAPIParams, tortoise_paginate
from teamgpt.schemata import ConversationsIn, ConversationsOut, ConversationsMessageIn, ConversationsMessageOut
from teamgpt.settings import (auth)
from teamgpt.util.entity_detector import EntityDetector
from teamgpt.util.gpt import ask, num_tokens_from_messages, msg_tiktoken_num

router = APIRouter(prefix='/api/v1/conversations', tags=['Conversations'])


@router.get("/message/test/{key}")
async def test(key: str):
    async def event_generator():
        openai.api_key = key
        async for chunk_msg in await openai.ChatCompletion.acreate(
                model='gpt-3.5-turbo',
                messages=[{"role": "user", "content": "hello"}, {
                    "role": "system", "content": "You're a chat robot"}],
                stream=True
        ):
            if 'content' in chunk_msg['choices'][0]['delta']:
                message = chunk_msg['choices'][0]['delta']['content']
            else:
                message = ''
            yield {'data': json.dumps({'message': message})}

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
    con_org = Conversations.filter(
        user=user_info, organization_id=organization_id, deleted_at__isnull=True)
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
        context_number: Union[int, None] = Query(default=5),
        encrypt_sensitive_data: Union[bool, None] = Query(default=False),
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    # 查询gpt-key配置信息,判断是否是系统用户
    key = ''
    org_info = await Organization.get_or_none(id=organization_id, deleted_at__isnull=True)
    # 判断组织支持的mode,限制gpt4小时发送条数
    default_gpt_model = [GptModel.GPT3, GptModel.GPT3TURBO, GptModel.GPT3TURBO0613,
                         GptModel.GPT3TURBO_16K_0613, GptModel.GPT3TURBO_16K]
    time_limit = 60
    count_limit = 10
    gpt_model_limit_list = [GptModel.GPT4, GptModel.GPT4_32K, GptModel.GPT4_0613, GptModel.GPT4_32K_0613]
    if model in gpt_model_limit_list:
        # 查询用户一小时内发送的条数
        count = await GptChatMessage.filter(
            user=user_info, created_at__gte=datetime.now() - timedelta(minutes=time_limit),
            model__in=gpt_model_limit_list,
            deleted_at__isnull=True).count()
        if count >= count_limit:
            raise HTTPException(status_code=420, detail=f'You can only send 10 messages in {time_limit} minutes')

    if org_info.gpt_models is not None:
        default_gpt_model = list(set(default_gpt_model + org_info.gpt_models))
    if model not in default_gpt_model:
        raise HTTPException(status_code=422, detail='The GPT model is not supported')
    # 判断是否有发送消息的权限
    plan_info = await org_payment_plan(org_info)
    if plan_info.is_send_msg is False:
        raise HTTPException(
            status_code=420, detail='Not allowed to send messages')
    if org_info is None:
        raise HTTPException(status_code=404, detail='Organization not found')
    if org_info.gpt_key_source is GptKeySource.SYSTEM:
        sys_gpt_key = await SysGPTKey.get_or_none(deleted_at__isnull=True)
        if sys_gpt_key is None:
            raise HTTPException(
                status_code=423, detail='SYS GPT key not found')
        key = sys_gpt_key.key
    else:
        gpt_key = await GPTKey.get_or_none(organization_id=organization_id, deleted_at__isnull=True)
        if gpt_key is None:
            if plan_info.sys_token is True:
                sys_gpt_key = await SysGPTKey.get_or_none(deleted_at__isnull=True)
                if sys_gpt_key is None:
                    raise HTTPException(
                        status_code=423, detail='SYS GPT key not found')
                key = sys_gpt_key.key
            else:
                if plan_info.is_try:
                    sys_gpt_key = await SysGPTKey.get_or_none(deleted_at__isnull=True)
                    if sys_gpt_key is None:
                        raise HTTPException(
                            status_code=423, detail='SYS GPT key not found')
                    key = sys_gpt_key.key
                else:
                    raise HTTPException(
                        status_code=423, detail='GPT key not found')
        else:
            key = gpt_key.key
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
            raise HTTPException(
                status_code=400, detail='Conversation format error')
    else:
        con_obj = await Conversations.get_or_none(id=conversation_id, deleted_at__isnull=True)
        if con_obj is None:
            raise HTTPException(
                status_code=404, detail='Conversation not found')

    # 循环消息插入数据库
    for conversations_input in conversations_input_list:
        if conversations_input.id is None:
            await ConversationsMessage.create(user=user_info, conversation_id=conversation_id,
                                              message=conversations_input.message,
                                              author_user=conversations_input.author_user,
                                              content_type=conversations_input.content_type,
                                              key=key,
                                              shown_message=conversations_input.shown_message,
                                              model=model
                                              )
        else:
            await ConversationsMessage.create(id=uuid.UUID(str(conversations_input.id)), user=user_info,
                                              conversation_id=conversation_id,
                                              message=conversations_input.message,
                                              author_user=conversations_input.author_user,
                                              content_type=conversations_input.content_type,
                                              shown_message=conversations_input.shown_message,
                                              key=key,
                                              model=model
                                              )
    # 查询前5条消息
    con_org = await ConversationsMessage.filter(user=user_info, conversation_id=conversation_id,
                                                deleted_at__isnull=True).order_by('-created_at').limit(context_number)
    detector = EntityDetector()

    for con in con_org:
        if encrypt_sensitive_data is True:
            detector.detect_entities(con.message)
            detector.map_items()
            content = detector.redact(con.message)

            print(content, detector.entity_registry_names)
        else:
            content = con.message
        message_log.append({'role': con.author_user, 'content': content})
    # 发送sse请求数据
    start_time = int(time.time())

    async def send_gpt():
        message = ''
        new_msg_obj_id = ''
        prompt_tokens = await num_tokens_from_messages(message_log[::-1], model=model)
        # 判断prompt_tokens如果超过4000,去除message_log最前面的数据,如果再超过4000则继续截取,直到小于4000,用一个新的message_log存储
        if prompt_tokens > 4000:
            while prompt_tokens > 4000:
                message_log.pop(-1)
                prompt_tokens = await num_tokens_from_messages(message_log[::-1], model=model)
        agen = ask(key, message_log[::-1], model, conversation_id)
        async for event in agen:
            event_data = json.loads(event['data'])
            if event_data['sta'] == 'run':
                message = message + event_data['message']
                if encrypt_sensitive_data is True:
                    message = detector.unredact(message)

                if new_msg_obj_id == '':
                    new_msg_obj = await ConversationsMessage.create(user=user_info, conversation_id=conversation_id,
                                                                    message=message,
                                                                    author_user=AutherUser.ASSISTANT,
                                                                    content_type=ContentType.TEXT,
                                                                    key=key,
                                                                    prompt_tokens=prompt_tokens,
                                                                    model=model
                                                                    )
                    new_msg_obj_id = str(new_msg_obj.id)
                event_data['msg_id'] = new_msg_obj_id
                event_data['sensitive_items'] = detector.entity_name_map
                event['data'] = json.dumps(event_data)
                yield event
            else:
                end_time = int(time.time())
                req_token_num = await msg_tiktoken_num(message, model=model)
                total_tokens = prompt_tokens + req_token_num

                await ConversationsMessage.filter(id=new_msg_obj_id).update(message=message,
                                                                            run_time=end_time - start_time,
                                                                            completion_tokens=req_token_num,
                                                                            total_tokens=total_tokens,
                                                                            )
                await GptChatMessage.create(in_message=json.dumps(message_log, ensure_ascii=False), out_message=message,
                                            key=key,
                                            user=user_info,
                                            organization_id=org_info.id, conversation_id=conversation_id, model=model)
                yield event
                await agen.aclose()
                detector.clear_values()

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
