from tortoise import models, fields
from datetime import datetime


class UserFiles(models.Model):
    """ Файлы пользователя """

    class FileStatuses:
        """ Статусы файла """
        DOWNLOADING = 'скачивается'
        PAUSE = 'пауза'
        ERROR = 'ошибка'
        DOWNLOADED = 'скачен'
        DELETE = 'удаление'

    id = fields.IntField(pk=True)
    file_name = fields.CharField(max_length=100)
    file = fields.ForeignKeyField('ftp.ScanFiles')
    user = fields.ForeignKeyField('users.Users')
    status = fields.CharField(max_length=12, default=FileStatuses.DOWNLOADING)
    size = fields.FloatField(default=0)
    process_id = fields.IntField()
    dt_downloading = fields.DatetimeField(default=datetime.now)
    dt_downloaded = fields.DatetimeField(null=True)
    access_all = fields.BooleanField(default=False)
    file_dir = fields.TextField()
    err_mess = fields.TextField()

    class Meta:
        table = 'user_files'

    def __str__(self):
        """ строковвое представление """
        return f'{self.id}'
