from tortoise import fields, models
from datetime import datetime


class ScanFiles(models.Model):
    """ Модель файлов на ФТП scanex """

    class Statuses:
        """ статусы файла на серверах сканекс """
        DOWNLOADING = 'скачивается со спутника'
        UPLOADING = 'готов к скачиванию'

    id = fields.IntField(pk=True)
    file_name = fields.TextField()
    size = fields.FloatField(default=0)
    date_add = fields.DatetimeField(default=datetime.now)
    station = fields.ForeignKeyField('ftp.ScanStations')
    status = fields.CharField(max_length=40, default=Statuses.DOWNLOADING)
    permits = fields.CharField(max_length=80)

    class Meta:
        table = 'scan_files'

    def __str__(self):
        """ Строковое представление модели """
        return str(self.id)
