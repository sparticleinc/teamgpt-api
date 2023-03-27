from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi_pagination import Page
from starlette.status import HTTP_204_NO_CONTENT
from typing import Union

from teamgpt.enums import GptModel
from teamgpt.models import User, Conversations, ConversationsMessage
from teamgpt.schemata import ConversationsIn, ConversationsOut, ConversationsMessageIn, ConversationsMessageOut
from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User
from teamgpt.parameters import ListAPIParams, tortoise_paginate

router = APIRouter(prefix='/conversations', tags=['Conversations'])


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
             dependencies=[Depends(auth.implicit_scheme)], response_model=Page[ConversationsMessageOut])
async def create_conversations_message(
        conversations_input_list: list[ConversationsMessageIn],
        organization_id: str,
        conversations_id: Union[str, None] = None,
        title: Union[str, None] = None,
        model: Union[GptModel, None] = Query(default=GptModel.GPT3TURBO),
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    if conversations_id is None:
        if len(conversations_input_list) > 1:
            new_obj = await Conversations.create(user=user_info, title=title, organization_id=organization_id,
                                                 model=model)
            conversations_id = new_obj.id
        else:
            raise HTTPException(status_code=400, detail='Conversation format error')
    else:
        con_obj = await Conversations.get_or_none(id=conversations_id, deleted_at__isnull=True)
        if con_obj is None:
            raise HTTPException(status_code=404, detail='Conversation not found')
    for conversations_input in conversations_input_list:
        await ConversationsMessage.create(user=user_info, conversation_id=conversations_id,
                                          message=conversations_input.message,
                                          author_user=conversations_input.author_user,
                                          content_type=conversations_input.content_type
                                          )

    con_org = ConversationsMessage.filter(user=user_info, conversation_id=conversations_id,
                                          deleted_at__isnull=True)
    params = ListAPIParams(page=1, page_size=10)
    params.order_by = 'created_at'
    con_list = await tortoise_paginate(con_org, params)
    return con_list


# get conversations message
@router.get('/message/{organization_id}/{conversations_id}',
            response_model=Page[ConversationsMessageIn], dependencies=[Depends(auth.implicit_scheme)])
async def get_conversations_message(
        conversations_id: str,
        user: Auth0User = Security(auth.get_user),
        params: ListAPIParams = Depends()
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    con_org = ConversationsMessage.filter(user=user_info, conversation_id=conversations_id,
                                          deleted_at__isnull=True)
    return await tortoise_paginate(con_org, params)
