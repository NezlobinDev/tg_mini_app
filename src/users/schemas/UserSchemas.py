from pydantic import BaseModel


class UserCreate(BaseModel):
    """ Схема создания пользователя """
    tg_id: int


class UserResponse(BaseModel):
    """ Схема информации о пользователе """
    id: int
    tg_id: int
    is_admin: bool


class UserTokenResponse(BaseModel):
    """ Схема информации о пользователе """
    access: str


class UserSecretCode(BaseModel):
    """ Схема информации о пользователе """
    user_id: int
    secret_code: str

