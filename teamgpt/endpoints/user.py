from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Security
from fastapi.responses import RedirectResponse
from fastapi_auth0 import Auth0User

from teamgpt.models import User
from teamgpt.schemata import UserOut
from teamgpt.settings import (AUTH0_CLIENT_ID, AUTH0_REDIRECT_URI,
                              AUTHORIZATION_URL, LOGOUT_URL, auth)
from teamgpt.util.auth0 import get_user_info

router = APIRouter(prefix='', tags=['users'])


@router.get('/login')
def do_login(state: Optional[str] = None):
    response_type_qs = urlencode({'response_type': 'token'})
    client_id_qs = urlencode({'client_id': AUTH0_CLIENT_ID})
    redirect_uri_qs = urlencode({'redirect_uri': AUTH0_REDIRECT_URI})
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
    user_obj = await User.get_or_none(user_id=user.id)
    if user_obj:
        return await UserOut.from_tortoise_orm(user_obj)
    user = await get_user_info(user.id)
    user_obj = await User.create(**user)
    return await UserOut.from_tortoise_orm(user_obj)
