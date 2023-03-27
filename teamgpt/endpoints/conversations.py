import uuid

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_pagination import Page
from teamgpt.enums import Role
from teamgpt.models import Organization, User, UserOrganization
from teamgpt.schemata import OrganizationOut, OrganizationIn, UserOrganizationOut, UserOut, UserOrganizationToOut
from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User
from teamgpt.parameters import ListAPIParams, tortoise_paginate

router = APIRouter(prefix='/api/v1/conversations', tags=['Conversations'])

#
# # 创建conversations
# @router.post('/', response_model=OrganizationOut)
# async def create_conversations(
#         organization: OrganizationIn,
#         current_user: Auth0User = Security(auth.get_current_user, scopes=['create:conversations'])
# ):
#     # 判断是否有创建组织的权限
#     if current_user.role != Role.ADMIN:
#         raise HTTPException(status_code=403, detail='Permission denied')
#     # 创建组织
#     organization = await Organization.create(**organization.dict())
#     return organization
#
#
# # 获取conversations
# @router.get('/', response_model=Page[OrganizationOut])
# async def get_conversations(
#         params: ListAPIParams = Depends(),
#         current_user: Auth0User = Security(auth.get_current_user, scopes=['read:conversations'])
# ):
#     # 判断是否有获取组织的权限
#     if current_user.role != Role.ADMIN:
#         raise HTTPException(status_code=403, detail='Permission denied')
#     # 获取组织
#     return await tortoise_paginate(params, Organization.all())
#
#
# # 删除conversations
# @router.delete('/{organization_id}', response_model=OrganizationOut)
# async def delete_conversations(
#         organization_id: uuid.UUID,
#         current_user: Auth0User = Security(auth.get_current_user, scopes=['delete:conversations'])
# ):
#     # 判断是否有删除组织的权限
#     if current_user.role != Role.ADMIN:
#         raise HTTPException(status_code=403, detail='Permission denied')
#     # 删除组织
#     organization = await Organization.get(id=organization_id)
#     await organization.soft_delete()
#     return organization
#
#
# # 修改conversations
# @router.put('/{organization_id}', response_model=OrganizationOut)
# async def update_conversations(
#         organization_id: uuid.UUID,
#         organization: OrganizationIn,
#         current_user: Auth0User = Security(auth.get_current_user, scopes=['update:conversations'])
# ):
#     # 判断是否有修改组织的权限
#     if current_user.role != Role.ADMIN:
#         raise HTTPException(status_code=403, detail='Permission denied')
#     # 修改组织
#     organization = await Organization.filter(id=organization_id).update(**organization.dict(exclude_unset=True))
#     return organization
