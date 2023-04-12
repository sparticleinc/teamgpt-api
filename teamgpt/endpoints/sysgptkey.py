import uuid

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi_auth0 import Auth0User
from fastapi_pagination import Page
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.models import GPTKey, User, Organization, SysGPTKey
from teamgpt.parameters import ListAPIParams, tortoise_paginate
from teamgpt.schemata import GPTKeyOut, GPTKeyIn, SysGPTKeyIn, SysGPTKeyOut
from teamgpt.settings import (auth)

router = APIRouter(prefix='/sys_gpt_key', tags=['SysGptKey'])


# create sys_gpt_key
@router.post(
    '',
    response_model=SysGPTKeyOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_sys_gpt_key(
        gpt_input: SysGPTKeyIn,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    if user_info.super is not True:
        raise HTTPException(
            status_code=400, detail='Not the admin')
    gpt_obj = await SysGPTKey.create(key=gpt_input.key, remarks=gpt_input.remarks)
    return await SysGPTKeyOut.from_tortoise_orm(gpt_obj)


# get sys_gpt_key
@router.get(
    '',
    response_model=Page[SysGPTKeyOut],
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_sys_gpt_key(
        user: Auth0User = Security(auth.get_user),
        params: ListAPIParams = Depends()
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    if user_info.super is not True:
        raise HTTPException(
            status_code=400, detail='Not the admin')
    gpt_key_list = SysGPTKey.filter(deleted_at__isnull=True)
    return await tortoise_paginate(gpt_key_list, params)


# del sys_gpt_key
@router.delete(
    '/{sys_gpt_key_id}',
    dependencies=[Depends(auth.implicit_scheme)], status_code=HTTP_204_NO_CONTENT
)
async def del_sys_gpt_key(
        sys_gpt_key_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    if user_info.super is not True:
        raise HTTPException(
            status_code=400, detail='Not the admin')
    gpt_obj = await SysGPTKey.get_or_none(id=uuid.UUID(sys_gpt_key_id), deleted_at__isnull=True)
    if gpt_obj is None:
        raise HTTPException(
            status_code=404, detail='Not found')
    await gpt_obj.soft_delete()
