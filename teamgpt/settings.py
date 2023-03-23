import os
from urllib.parse import quote, urlencode
from fastapi_auth0 import Auth0


def urlencode_for_db(s): return quote(str(s), safe='')


def import_temp_env():
    if not os.path.exists('.env'):
        return
    print('[info] Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            key, value = var[0].strip(), var[1].strip()
            os.environ[key] = value


import_temp_env()

# Database settings
DB_HOST = os.getenv(
    'DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'circleo')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'circleo')
DB_NAME = os.getenv('DB_NAME', 'mygpt')
DB_CHARSET = os.getenv('DB_CHARSET', 'utf8')
DB_URL = 'postgres://{username}:{pwd}@{host}:{port}/{dbname}'.format(
    username=urlencode_for_db(DB_USER),
    pwd=urlencode_for_db(DB_PASSWORD),
    host=urlencode_for_db(DB_HOST),
    port=urlencode_for_db(DB_PORT),
    dbname=urlencode_for_db(DB_NAME),
)

# auth0
# AUTH0_DOMAIN = os.getenv(
#     'AUTH0_DOMAIN', 'dev-1x5li4ewlxn3t8ed.jp.auth0.com')
# AUTH0_API_AUDIENCE = os.getenv('AUTH0_API_AUDIENCE', 'https://teamgpt.felo.me')
# AUTH0_CLIENT_ID = os.getenv(
#     'AUTH0_CLIENT_ID', 'XGEBP8CV9tOy1BW3o0XVBPoilLm0QkHp')
# AUTH0_REDIRECT_URI = os.getenv(
#     'AUTH0_REDIRECT_URI', 'http://localhost:8000/docs/oauth2-redirect')
# AUTH0_LOGOUT_REDIRECT_URI = os.getenv(
#     'AUTH0_LOGOUT_REDIRECT_URI', 'http://localhost:8000/docs/oauth2-redirect')
#
# AUTH0_ADMIN_CLIENT_ID = os.getenv(
#     'AUTH0_ADMIN_CLIENT_ID', 'XGEBP8CV9tOy1BW3o0XVBPoilLm0QkHp')
# AUTH0_ADMIN_CLIENT_SRCRET = os.getenv(
#     'AUTH0_ADMIN_CLIENT_SRCRET', 'LcmMatiOTA5ebF2bu6l0rLLwMQd7bMz65JneTngtOxGh0pP6zyfgahyQe4V30k4o')
# AUTH0_ADMIN_API_AUDIENCE = os.getenv(
#     'AUTH0_ADMIN_API_AUDIENCE', 'https://dev-1x5li4ewlxn3t8ed.jp.auth0.com/api/v2/')

AUTH0_DOMAIN = 'dev-1x5li4ewlxn3t8ed.jp.auth0.com'
AUTH0_API_AUDIENCE = os.getenv('AUTH0_API_AUDIENCE', 'https://teamgpt.felo.me')
AUTH0_CLIENT_ID = os.getenv(
    'AUTH0_CLIENT_ID', 'XGEBP8CV9tOy1BW3o0XVBPoilLm0QkHp')
AUTH0_REDIRECT_URI = os.getenv(
    'AUTH0_REDIRECT_URI', 'http://localhost:8000/docs/oauth2-redirect')
AUTH0_LOGOUT_REDIRECT_URI = os.getenv(
    'AUTH0_LOGOUT_REDIRECT_URI', 'http://localhost:8000/docs/oauth2-redirect')

AUTH0_ADMIN_CLIENT_ID = os.getenv(
    'AUTH0_ADMIN_CLIENT_ID', 'XGEBP8CV9tOy1BW3o0XVBPoilLm0QkHp')
AUTH0_ADMIN_CLIENT_SRCRET = os.getenv(
    'AUTH0_ADMIN_CLIENT_SRCRET', 'LcmMatiOTA5ebF2bu6l0rLLwMQd7bMz65JneTngtOxGh0pP6zyfgahyQe4V30k4o')
AUTH0_ADMIN_API_AUDIENCE = os.getenv(
    'AUTH0_ADMIN_API_AUDIENCE', 'https://dev-1x5li4ewlxn3t8ed.jp.auth0.com/api/v2/')

auth = Auth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE, scopes={})

# oauth2 config for login&logout
AUTHORIZATION_URL_QS = urlencode({'audience': AUTH0_API_AUDIENCE})
AUTHORIZATION_URL = f'https://{AUTH0_DOMAIN}/authorize?{AUTHORIZATION_URL_QS}'
LOGOUT_URL = f'https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo={AUTH0_LOGOUT_REDIRECT_URI}'

# TortoiseORM settings
TORTOISE_ORM = {
    'connections': {
        'default': DB_URL,
    },
    'apps': {
        'models': {
            'models': ['teamgpt.models', 'aerich.models'],
            'default_connection': 'default',
        },
    },
}


def api_key() -> str:
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(48))
    return f'ak-{token}'
