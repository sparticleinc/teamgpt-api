from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_auth0 import Auth0User
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.models import User, UserOrganization, Organization
from teamgpt.schemata import UserOut
from teamgpt.settings import (AUTH0_CLIENT_ID, AUTH0_REDIRECT_URI,
                              AUTHORIZATION_URL, LOGOUT_URL, auth)
from teamgpt.util.auth0 import get_user_info

router = APIRouter(prefix='', tags=['Users'])


@router.get('/login')
def do_login(state: Optional[str] = None, url: Optional[str] = None):
    response_type_qs = urlencode({'response_type': 'token'})
    client_id_qs = urlencode({'client_id': AUTH0_CLIENT_ID})
    if url is None:
        redirect_uri_qs = urlencode({'redirect_uri': AUTH0_REDIRECT_URI})
    else:
        redirect_uri_qs = urlencode({'redirect_uri': url})
    state_qs = urlencode({'state': state})
    auth_url = f'{AUTHORIZATION_URL}&{response_type_qs}&{client_id_qs}&{redirect_uri_qs}&{state_qs}'
    return RedirectResponse(url=auth_url, status_code=302)


@router.get('/logout')
def do_logout():
    return RedirectResponse(url=LOGOUT_URL, status_code=302)


@router.get(
    '/users/me',
    response_model=UserOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_current_user(user: Auth0User = Security(auth.get_user)):
    auth_user = await get_user_info(user.id)
    user_obj = await User.get_or_none(email=auth_user['email'])
    if user_obj:
        await User.filter(id=user_obj.id).update(user_id=user.id, name=auth_user['name'],
                                                 picture=auth_user['picture'],
                                                 nickname=auth_user['nickname'])
        new_user_obj = await User.get_or_none(email=auth_user['email'])
        return await UserOut.from_tortoise_orm(new_user_obj)
    user_obj = await User.create(**auth_user)
    return await UserOut.from_tortoise_orm(user_obj)


# 用户绑定当前所在组织
@router.post(
    '/bind/{organization_id}',
    dependencies=[Depends(auth.implicit_scheme)], status_code=HTTP_204_NO_CONTENT,
)
async def bind_user_organization(
        organization_id: str,
        user: Auth0User = Security(auth.get_user)
):
    user_obj = await User.get_or_none(user_id=user.id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    org_obj = await Organization.get_or_none(id=organization_id)
    if org_obj is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    # 查询用户是否在这个组织中
    user_org = await UserOrganization.get_or_none(user_id=user_obj.id, organization_id=organization_id)
    if user_org is None:
        raise HTTPException(status_code=404, detail="User not found in this organization")
    await User.filter(id=user_obj.id).update(current_organization=organization_id)
