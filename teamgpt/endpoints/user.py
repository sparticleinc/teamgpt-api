from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_auth0 import Auth0User
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.endpoints.stripe import org_payment_plan
from teamgpt.models import User, UserOrganization, Organization
from teamgpt.schemata import UserToOut
from teamgpt.settings import (AUTH0_CLIENT_ID, AUTH0_REDIRECT_URI,
                              AUTHORIZATION_URL, LOGOUT_URL, auth)
from teamgpt.util.auth0 import get_user_info

router = APIRouter(prefix='/api/v1', tags=['Users'])


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
def do_logout(url: Optional[str] = None):
    if url is None:
        return RedirectResponse(url=LOGOUT_URL, status_code=302)
    else:
        return RedirectResponse(url=url, status_code=302)


@router.get(
    '/users/me',
    response_model=UserToOut,
    dependencies=[Depends(auth.implicit_scheme)]
)
async def get_current_user(user: Auth0User = Security(auth.get_user), code: Optional[str] = None):
    auth_user = await get_user_info(user.id)
    join_sta = ''
    user_obj = await User.get_or_none(user_id=user.id)
    if user_obj is None:
        user_obj = await User.create(**auth_user)
        # # 创建默认组织
        # org_name = auth_user['nickname'] + '_' + random_run.number(4)
        # org_obj = await Organization.create(name=org_name, deleted_at__isnull=True,
        #                                     defaults={'picture': '',
        #                                               'creator': user_obj,
        #                                               'gpt_key_source': ''})
        # await UserOrganization.create(user=user_obj, organization_id=org_obj.id, role=Role.CREATOR)
        # # 插入系统的aiprm
        # await update_organization_id(org_obj.id)
    if code is not None:
        org_obj = await Organization.get_or_none(code=code, deleted_at__isnull=True,
                                                 code_expiration_time__gt=datetime.now())
        if org_obj is not None:
            user_org = await UserOrganization.get_or_none(user_id=user_obj.id,
                                                          organization_id=org_obj.id, deleted_at__isnull=True)
            plan_info = await org_payment_plan(org_obj)
            if user_org is None and plan_info.is_join is True:
                join_sta = 'success'
                await UserOrganization.create(user_id=user_obj.id, organization_id=org_obj.id, role='member')
                await User.filter(id=user_obj.id).update(current_organization=org_obj.id)
            else:
                join_sta = 'maximum'
        else:
            join_sta = 'code_error'
    else:
        join_sta = 'no_code'
    user_out = UserToOut.from_orm(user_obj)
    user_out.join_sta = join_sta
    return user_out


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
        raise HTTPException(
            status_code=404, detail="User not found in this organization")
    await User.filter(id=user_obj.id).update(current_organization=organization_id)
