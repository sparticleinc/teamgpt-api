from fastapi import APIRouter, Body, Depends, HTTPException, Security

from teamgpt.models import Organization, User
from teamgpt.schemata import OrganizationOut, OrganizationIn
from teamgpt.settings import (AUTH0_CLIENT_ID, AUTH0_REDIRECT_URI,
                              AUTHORIZATION_URL, LOGOUT_URL, auth)
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
    org_info = await Organization.get_or_none(name=org_input.name)
    if org_info is not None:
        raise HTTPException(status_code=400, detail='Organization name already exists')
    user_info = await User.get_or_none(user_id=user.id)
    new_org_obj = await Organization.create(name=org_input.name, picture=org_input.picture, creator=user_info)
    return await OrganizationOut.from_tortoise_orm(new_org_obj)
