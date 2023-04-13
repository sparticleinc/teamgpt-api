import uuid

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi_auth0 import Auth0User
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.models import User, AiCharacter, UserOrganization
from teamgpt.parameters import Page, ListAPIParams, tortoise_paginate
from teamgpt.schemata import AiCharacterIn, AiCharacterOut, AiCharacterToOut
from teamgpt.settings import (auth)

router = APIRouter(prefix='/api/v1/ai_character', tags=['AiCharacter'])


# create ai_character
@router.post(
    '/{organization_id}',
    response_model=AiCharacterOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_ai_character(
        ai_character_input: AiCharacterIn,
        organization_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    user_organization = await UserOrganization.get_or_none(user_id=user_info.id, organization_id=uuid.UUID(
        organization_id), deleted_at__isnull=True)
    if user_organization is None:
        raise HTTPException(
            status_code=400, detail='Not the member')
    ai_character_obj = await AiCharacter.create(
        title=ai_character_input.title,
        description=ai_character_input.description,
        instruction=ai_character_input.instruction,
        organization_id=uuid.UUID(organization_id),
        user_id=user_info.id
    )
    return await AiCharacterOut.from_tortoise_orm(ai_character_obj)


# delete ai_character
@router.delete(
    '/{ai_character_id}',
    dependencies=[Depends(auth.implicit_scheme)],
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_ai_character(
        ai_character_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    ai_character_obj = await AiCharacter.get_or_none(id=uuid.UUID(ai_character_id), user_id=user_info.id,
                                                     deleted_at__isnull=True)
    if ai_character_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await ai_character_obj.soft_delete()


# edit ai_character
@router.put(
    '/{ai_character_id}',
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def edit_ai_character(
        ai_character_id: str,
        ai_character_input: AiCharacterIn,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    ai_character_obj = await AiCharacter.get_or_none(id=uuid.UUID(ai_character_id), user_id=user_info.id,
                                                     deleted_at__isnull=True)
    if ai_character_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await AiCharacter.filter(id=ai_character_obj.id).update(
        title=ai_character_input.title,
        description=ai_character_input.description,
        instruction=ai_character_input.instruction,
    )


# get org ai_character
@router.get(
    '/{organization_id}',
    response_model=Page[AiCharacterToOut],
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_org_ai_character(
        organization_id: str,
        user: Auth0User = Security(auth.get_user),
        params: ListAPIParams = Depends()
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    user_organization = await UserOrganization.get_or_none(user_id=user_info.id, organization_id=uuid.UUID(
        organization_id))
    if user_organization is None:
        raise HTTPException(
            status_code=400, detail='Not the member')
    ai_org = AiCharacter.filter(organization_id=uuid.UUID(organization_id), deleted_at__isnull=True)
    return await tortoise_paginate(ai_org, params, ['user'])
