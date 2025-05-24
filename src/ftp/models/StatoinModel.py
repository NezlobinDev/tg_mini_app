from tortoise import models, fields


class ScanStations(models.Model):
    """
    Станции приема файлов со спутника

    id: Первичный ключ
    name: Название станции(выводимое клиенту)
    is_ssl: Установить ли параметры ssl при подключении к станции
    station_url: Url подключения к станции
    lgin: Логин подключения к станции
    pwd: Пароль подключения к станции
    file_format: Формат файлов на сервере
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=5, unique=True)
    is_ssl = fields.BooleanField(default=True)
    station_url = fields.TextField()
    login = fields.CharField(max_length=100)
    pwd = fields.CharField(max_length=100)
    patch = fields.CharField(max_length=100, null=True)
    file_format = fields.CharField(default='.dat', max_length=5)

    class Meta:
        table = 'scan_stations'

    def __str__(self):
        """ Строковое представление модели """
        return str(self.id)
