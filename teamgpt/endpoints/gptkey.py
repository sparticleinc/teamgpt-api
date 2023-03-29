import uuid

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi_auth0 import Auth0User

from teamgpt.models import GPTKey, User, Organization
from teamgpt.schemata import GPTKeyOut, GPTKeyIn
from teamgpt.settings import (auth)

router = APIRouter(prefix='/gpt_key', tags=['GptKey'])


@router.post(
    '',
    response_model=GPTKeyOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def bind_gpt(
        gpt_input: GPTKeyIn,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id)
    organization_info = await Organization.get_or_none(id=uuid.UUID(gpt_input.organization_id))
    if user_info.id != organization_info.creator_id:
        raise HTTPException(
            status_code=400, detail='Not the creator')
    gpt_obj = await GPTKey.get_or_none(organization_id=uuid.UUID(gpt_input.organization_id))
    if gpt_obj:
        await GPTKey.filter(id=gpt_obj.id).update(key=gpt_input.key)
    else:
        gpt_obj = await GPTKey.create(key=gpt_input.key, organization_id=uuid.UUID(gpt_input.organization_id))
    return await GPTKeyOut.from_tortoise_orm(gpt_obj)


@router.get(
    '/{organization_id}',
    response_model=GPTKeyOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_organization_gpt_key(
        organization_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id)
    organization_info = await Organization.get_or_none(id=uuid.UUID(organization_id))
    if user_info.id != organization_info.creator_id:
        raise HTTPException(
            status_code=400, detail='Not the creator')
    gpt_obj = await GPTKey.get_or_none(organization_id=uuid.UUID(organization_id))
    if gpt_obj:
        return await GPTKeyOut.from_tortoise_orm(gpt_obj)
    else:
        raise HTTPException(
            status_code=404, detail='Not found')
