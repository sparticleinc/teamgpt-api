import logging
from auth0 import Auth0Error
from auth0.authentication import GetToken
from auth0.management import Auth0
from fastapi import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from teamgpt.settings import (AUTH0_ADMIN_API_AUDIENCE, AUTH0_ADMIN_CLIENT_ID,
                              AUTH0_ADMIN_CLIENT_SRCRET, AUTH0_DOMAIN)


async def get_user_info(user_id: str) -> dict:
    auth0_token = GetToken(
        AUTH0_DOMAIN,
        AUTH0_ADMIN_CLIENT_ID,
        AUTH0_ADMIN_CLIENT_SRCRET
    ).client_credentials(AUTH0_ADMIN_API_AUDIENCE)
    access_token = auth0_token['access_token']
    auth0 = Auth0(AUTH0_DOMAIN, access_token)
    try:
        user_info = auth0.users.get(id=user_id)
    except Auth0Error as e:
        logging.error(f'create client error:{e}')
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return user_info
