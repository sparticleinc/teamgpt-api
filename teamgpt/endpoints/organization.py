import uuid

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_pagination import Page
from teamgpt.enums import Role
from teamgpt.models import Organization, User, UserOrganization
from teamgpt.schemata import OrganizationOut, OrganizationIn, UserOrganizationToOut
from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User
from teamgpt.parameters import ListAPIParams, tortoise_paginate

router = APIRouter(prefix='/organization', tags=['Organization'])


@router.post(
    '',
    response_model=OrganizationOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def create_organization(
        org_input: OrganizationIn,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    new_org_obj, created = await Organization.get_or_create(name=org_input.name, deleted_at__isnull=True,
                                                            defaults={'picture': org_input.picture,
                                                                      'creator': user_info})
    if not created:
        raise HTTPException(
            status_code=400, detail='Organization name already exists')
    await UserOrganization.create(user=user_info, organization_id=new_org_obj.id, role=Role.CREATOR)

    return await OrganizationOut.from_tortoise_orm(new_org_obj)


@router.delete(
    '/{org_id}',
    response_model=OrganizationOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def delete_organization(
        org_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    org_obj = await Organization.get_or_none(id=org_id, deleted_at__isnull=True)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization id already exists')
    if org_obj.creator_id != user_info.id:
        raise HTTPException(
            status_code=403, detail='User not authorized to delete this organization')
    await org_obj.soft_delete()
    return await OrganizationOut.from_tortoise_orm(org_obj)


@router.get(
    '/{org_id}',
    response_model=OrganizationOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_organization(
        org_id: str,
):
    org_obj = await Organization.get_or_none(id=org_id, deleted_at__isnull=True)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization id not found')
    return await OrganizationOut.from_tortoise_orm(org_obj)


@router.put(
    '/{org_id}',
    response_model=OrganizationOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def update_organization(
        org_id: str,
        org_input: OrganizationIn,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    org_obj = await Organization.get_or_none(id=org_id, deleted_at__isnull=True)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization id not found')
    if org_obj.creator_id != user_info.id:
        raise HTTPException(
            status_code=403, detail='User not authorized to update this organization')
    await org_obj.update_from_dict(org_input.dict()).save()
    return await OrganizationOut.from_tortoise_orm(org_obj)


@router.get(
    '/{org_id}/users',
    dependencies=[Depends(auth.implicit_scheme)],
    response_model=Page[UserOrganizationToOut]
)
async def get_users_in_organization(
        org_id: str,
        params: ListAPIParams = Depends(),
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    org_obj = await Organization.get_or_none(id=org_id, deleted_at__isnull=True)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization not found')
    me_user_organization = await UserOrganization.get_or_none(organization_id=org_obj.id, user_id=user_info.id,
                                                              deleted_at__isnull=True)
    if not me_user_organization:
        raise HTTPException(
            status_code=404, detail='User not found in this organization')
    queryset = UserOrganization.filter(
        organization=org_obj.id, deleted_at__isnull=True)
    return await tortoise_paginate(queryset, params, ['organization', 'user'])


# 邀请人加入Organization
@router.post(
    '/{org_id}/invite',
    response_model=OrganizationOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def invite_user_to_organization(
        org_id: str,
        email: str,
        user: Auth0User = Security(auth.get_user)
):
    create_user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    user_info = await User.get_or_none(email=email, deleted_at__isnull=True)
    org_obj = await Organization.get_or_none(id=org_id, deleted_at__isnull=True)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization not found')
    if org_obj.creator_id != create_user_info.id:
        raise HTTPException(
            status_code=403, detail='User not authorized to invite this organization')
    if not user_info:
        user_info = await User.create(email=email, user_id=uuid.uuid4())
    user_org_info = await UserOrganization.get_or_none(user=user_info, organization_id=org_obj.id,
                                                       deleted_at__isnull=True)
    if user_org_info:
        raise HTTPException(
            status_code=400, detail='User already in this organization')
    await UserOrganization.create(user=user_info, organization_id=org_obj.id, role=Role.MEMBER)
    return await OrganizationOut.from_tortoise_orm(org_obj)


# 查询自己在哪些Organization
@router.get(
    '/me/info',
    dependencies=[Depends(auth.implicit_scheme)],
    response_model=Page[UserOrganizationToOut]
)
async def get_my_organizations(
        params: ListAPIParams = Depends(),
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    queryset = UserOrganization.filter(
        user=user_info.id, deleted_at__isnull=True)
    return await tortoise_paginate(queryset, params, ['organization', 'user'])
