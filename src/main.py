from fastapi import FastAPI, Request, Response, status
from tortoise import Tortoise
from users.api.http_view import list_user_routers
from users.api.ws_view import list_user_ws_routers
from ftp.api.http_view import list_ftp_routers
from app.settings.db import db_init
import jwt
from fastapi.middleware.cors import CORSMiddleware
from app.settings.base import SECRET_KEY, ALGORITHM, BOT
from fastapi.staticfiles import StaticFiles
from app.settings.base import templates


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    '/static',
    StaticFiles(directory='web_interface/static'),
    name='static',
)


@app.get('/web_app')
async def open_web_app(request: Request):
    """ Открыть главную страницу приложения """
    return templates.TemplateResponse('index.html', {'request': request})


@app.middleware('http')
async def jwt_middleware(request: Request, call_next):
    """ мидлварь получения токена """
    from users.models import Users
    request.state.bot = BOT
    request.state.user = None
    exclude_patch = [
        '/users/reg/',
        '/users/auth/get_code/',
        '/users/auth/enter_code/',
        '/docs', '/openapi.json', '/web_app', '/static',
        '.ico',
    ]
    for e_path in exclude_patch:
        if e_path in request.url.path:
            response = await call_next(request)
            return response

    token = request.headers.get('Authorization', request.cookies.get('Authorization'))
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = await Users.get_or_none(id=payload.get('u_id', 0))
        except (jwt.PyJWTError, IndexError):
            return Response(content='Invalid token', status_code=401)
        if request.state.user is None:
            return Response(content='Invalid auth', status_code=401)
    else:
        return Response(content='Token is missing', status_code=401)

    if request.state.user and request.state.user.is_active is False:
        return Response(content='Not Allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    response = await call_next(request)
    return response


@app.on_event('startup')
async def startup():
    """ При старте """
    routers_cfg = {
        '/api': [
            list_user_routers,
            list_ftp_routers,
        ],
        '/ws': [
            list_user_ws_routers
        ]
    }
    await db_init(app)
    for prefix, routers in routers_cfg.items():
        for app_routers in routers:
            for router in app_routers:
                app.include_router(router, prefix=prefix)


@app.on_event('shutdown')
async def shutdown():
    """ При выключении """
    await Tortoise.close_connections()

