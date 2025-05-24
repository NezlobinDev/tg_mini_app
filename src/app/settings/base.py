from fastapi.templating import Jinja2Templates
from aiogram import Bot

with open('app/settings/.env', 'r') as env:
    list_env = env.read().split('\n')
    env_data = {
        el.split('=')[0]: el.split('=')[1]
        for el in list_env
    }

templates = Jinja2Templates(directory='web_interface/templates')

SECRET_KEY = env_data.get('SECRET_KEY', '')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = (60 * 60) * 24
TG_FTP_BOT_TOKEN = env_data.get('TG_FTP_BOT_TOKEN', '')
DOMAIN_ADDR = env_data.get('DOMAIN_ADDR', 'http://127.0.0.1:8000')
BOT = Bot(token=TG_FTP_BOT_TOKEN)
