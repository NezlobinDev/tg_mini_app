from app.settings.installed_app import APPS
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import os


MODELS = [f'{app}.models' for app in APPS if os.path.isdir(f'{app}/models')]
TORTOISE_ORM = {
    'connections': {
        'default': 'sqlite://db.sqlite3',
    },
    'apps': {
        model.split('.')[0]: {
            'models': [model],
            'default_connection': 'default',
        }
        for model in MODELS
    },
    'timezone': 'Europe/Moscow',
}


async def db_init(app: FastAPI):
    """ Инициализация базы данных """
    register_tortoise(
        app,
        db_url='sqlite://db.sqlite3',
        modules={app_name: app_config['models'] for app_name, app_config in TORTOISE_ORM['apps'].items()},
        generate_schemas=True,
        add_exception_handlers=True,
    )
