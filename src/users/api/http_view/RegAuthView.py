from users.models import Users, AuthCodes, UserFiles
from users.schemas import UserCreate, UserResponse
from fastapi import HTTPException, Request, Response
from random import randint
from users.api.utils import get_recent_auth_codes
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from utils.jwt_auth import create_access_token
from fastapi.responses import HTMLResponse
from tg_bot import send_user_url_button
import os
from app.settings.base import DOMAIN_ADDR
from fastapi.responses import JSONResponse


users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post('/reg/', response_model=UserResponse)
async def user_reg(user: UserCreate):
    """ Регистрация нового пользователя """
    user_obj = await Users.create(tg_id=user.tg_id)
    dir_name = user_obj.get_dir()
    try:
        os.mkdir(dir_name)
    except (FileExistsError, OSError):
        pass

    try:
        os.chmod(dir_name, 0o755)
    except OSError:
        pass
    return user_obj


@users_router.get('/auth/get_code/', response_model=UserResponse)
async def user_get_code(request: Request, user_id: int):
    """ Отправить 6 значиный код в телеграм """
    user = await Users.get_or_none(tg_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User  not found')
    s_code = str(randint(100000, 999999))
    await AuthCodes.create(user=user, sicret_code=s_code)

    old_url = f'{DOMAIN_ADDR}/api/users/auth/enter_code/?user_id={user_id}&secret_code={s_code}'
    await send_user_url_button(
        bot=request.state.bot,
        user_id=user_id,
        btn_url='https://google.com',
        mess=f'Нажмите на кнопку для авторизации: {s_code}\n{old_url}',
        btn_mess=f'Авторизация: {s_code}',
    )
    return user


@users_router.get('/auth/enter_code/', response_class=HTMLResponse)
async def user_enter_code(response: Response, request: Request, user_id: int, secret_code: str):
    """ Авторизация по 6 значному коду """
    user = await Users.get_or_none(tg_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    secret_code: AuthCodes = await get_recent_auth_codes(user, secret_code)
    if secret_code is None:
        raise HTTPException(status_code=403, detail='Not code')
    await secret_code.delete()

    token = create_access_token({'u_id': user.id})
    response.set_cookie(key='Authorization', value=token)

    resp = RedirectResponse(url='/web_app')
    resp.set_cookie(key='Authorization', value=token)

    await send_user_url_button(
        bot=request.state.bot,
        user_id=user_id,
        btn_url='https://vk.com/feed',
        mess='Вы успешно авторизовались',
        btn_mess='Открыть miniapp',
    )

    return resp


@users_router.get('/me/', response_model=UserResponse)
async def user_get_code(request: Request):
    user = request.state.user
    u_files = await UserFiles.filter(user=user, status=UserFiles.FileStatuses.DOWNLOADED).count()
    return JSONResponse(
        content={
            'id': user.id,
            'tg_id': user.tg_id,
            'is_admin': user.is_admin,
            'avg_download': u_files,
        },
        status_code=200,
    )
