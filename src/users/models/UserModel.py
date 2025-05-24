from tortoise import fields, models
from datetime import datetime


class Users(models.Model):
    """ Модель пользователей """

    id = fields.IntField(pk=True)
    tg_id = fields.IntField(unique=True)
    is_active = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)

    def get_dir(self):
        """ получить директорию пользоателя """
        return f'ftpdata/user_{self.id}'

    class Meta:
        table = 'users'

    def __str__(self):
        """ Строковое представление модели """
        return f'{self.id}'


class AuthCodes(models.Model):
    """ Модель временных кодов авторизации """

    id = fields.IntField(pk=True)
    sicret_code = fields.CharField(max_length=7)
    user = fields.ForeignKeyField('users.Users', related_name='auth_codes')
    date_add = fields.DatetimeField(default=datetime.now)
    is_used = fields.BooleanField(default=False)

    class Meta:
        table = 'auth_codes'

    def __str__(self):
        """ строковвое представление """
        return f'{self.id}'
