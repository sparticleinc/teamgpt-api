import uuid

from fastapi import APIRouter, Depends, HTTPException, Security

from teamgpt.enums import Role
from teamgpt.models import Organization, User, UserOrganization
from teamgpt.schemata import OrganizationOut, OrganizationIn
from teamgpt.settings import (auth)
from fastapi_auth0 import Auth0User

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
    user_info = await User.get_or_none(user_id=user.id)
    new_org_obj, created = await Organization.get_or_create(name=org_input.name, defaults={'picture': org_input.picture,
                                                                                           'creator': user_info})
    await UserOrganization.create(user=user_info, organization_id=new_org_obj.id, role=Role.CREATOR)
    if not created:
        raise HTTPException(
            status_code=400, detail='Organization name already exists')
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
    user_info = await User.get_or_none(user_id=user.id)
    org_obj = await Organization.get_or_none(id=org_id)
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
    org_obj = await Organization.get_or_none(id=org_id)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization not found')
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
    user_info = await User.get_or_none(user_id=user.id)
    org_obj = await Organization.get_or_none(id=org_id)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization not found')
    if org_obj.creator_id != user_info.id:
        raise HTTPException(
            status_code=403, detail='User not authorized to update this organization')
    await org_obj.update_from_dict(org_input.dict()).save()
    return await OrganizationOut.from_tortoise_orm(org_obj)


@router.get(
    '/{org_id}/users',
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_users_in_organization(
        org_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_info = await User.get_or_none(user_id=user.id)
    org_obj = await Organization.get_or_none(id=org_id)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization not found')
    info = await UserOrganization.filter(user_id=user_info.id, organization_id=org_obj.id).all()
    return info


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
    create_user_info = await User.get_or_none(user_id=user.id)
    user_info = await User.get_or_none(email=email)
    org_obj = await Organization.get_or_none(id=org_id)
    if not org_obj:
        raise HTTPException(
            status_code=404, detail='Organization not found')
    if org_obj.creator_id != create_user_info.id:
        raise HTTPException(
            status_code=403, detail='User not authorized to invite this organization')
    if not user_info:
        user_info = await User.create(email=email, user_id=uuid.uuid4())
    await UserOrganization.create(user=user_info, organization_id=org_obj.id, role=Role.MEMBER)
    return await OrganizationOut.from_tortoise_orm(org_obj)
