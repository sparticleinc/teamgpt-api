import nest_asyncio
from starlette import status
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from teamgpt.endpoints import router
from teamgpt.settings import TORTOISE_ORM
from fastapi.openapi.docs import (get_swagger_ui_html,
                                  get_swagger_ui_oauth2_redirect_html)
from fastapi import FastAPI, Request

nest_asyncio.apply()

app = FastAPI()

app.include_router(router)
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


async def general_exception_handler(request, err):
    base_error_message = f'Failed to execute: {request.method}: {request.url}'
    return JSONResponse({
        'detail': str(err),
        'message': base_error_message
    }, status_code=status.HTTP_400_BAD_REQUEST)


app.add_middleware(
    ServerErrorMiddleware,
    handler=general_exception_handler,
)


def get_openapi_url(request: Request, openapi_url: str) -> str:
    root_path = request.scope.get('root_path')
    return f'{root_path}/{openapi_url}' if root_path else openapi_url


@app.get('/docs-swagger', include_in_schema=False)
async def get_documentation(request: Request):
    root_path = request.scope.get('root_path')
    return get_swagger_ui_html(
        openapi_url=get_openapi_url(request, 'openapi.json'),
        oauth2_redirect_url=f'{root_path}/docs-swagger/oauth2-redirect',
        title='Documentation',
    )


@app.get('/docs-swagger/oauth2-redirect', include_in_schema=False)
async def oauth2_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get('/')
def read_root():
    return 'hello'
