from users.models import AuthCodes
from datetime import datetime,timedelta


async def get_recent_auth_codes(user, secret_code):
    """ Получить код авторизации, время жизни токена 2 минуты """
    two_minutes_ago = datetime.now() - timedelta(minutes=2)
    return await AuthCodes.filter(
        user=user,
        date_add__gte=two_minutes_ago,
        is_used=False,
        sicret_code=secret_code,
    ).order_by('-date_add').limit(1).first()
