import uuid

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_pagination import Page
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.enums import Role
from teamgpt.models import Organization, User, UserOrganization, Conversations
from teamgpt.schemata import ConversationsIn, ConversationsOut
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
