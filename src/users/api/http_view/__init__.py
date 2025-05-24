from users.api.http_view.RegAuthView import users_router
from users.api.http_view.FtpFilesView import ftp_router

list_user_routers = [
    users_router,
    ftp_router,
]

__all__ = ['list_user_routers']
