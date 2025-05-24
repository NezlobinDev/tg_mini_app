from ftp.models import ScanFiles
from ftp.utils.commands import list_files_ftp
from users.models import Users
from app.settings.base import BOT


async def task_check_new_files():
    """ Проверка файлов на серверах сканекса """
    all_files_data = await list_files_ftp()

    # Получаем файлы из базы данных
    existing_files = await ScanFiles.all()  # Получаем все файлы из базы данных
    existing_file_map = {file.file_name: file for file in
                         existing_files}  # Словарь для быстрого доступа к существующим файлам

    uploading_files = set()
    # Фильтруем новые файлы
    for f_name, f_data in all_files_data.items():
        file_name = f_data['name']
        file_size = f_data['size']
        file_date = f_data['date']
        file_station = f_data['station']
        permits = f_data['permits']

        if file_name in existing_file_map:
            existing_file = existing_file_map[file_name]
            # Проверяем размер файла
            if int(existing_file.size) != int(file_size):
                # Если размеры отличаются, обновляем размер файла в БД
                existing_file.size = file_size
                await existing_file.save()
            else:
                # Если размеры равны, меняем статус с DOWNLOADING на UPLOADING
                # Уведомляем пользователей в телеграм что появился новый файл и его можно скачать
                existing_file.status = ScanFiles.Statuses.UPLOADING
                await existing_file.save()
                uploading_files.add(file_name)
        else:
            # Если файл не существует, добавляем его в базу данных
            await ScanFiles.create(
                file_name=file_name,
                date_add=file_date,
                status=ScanFiles.Statuses.DOWNLOADING,
                size=file_size,
                station=file_station,
                permits=' | '.join(permits),
            )

    avg_uploading_files = len(uploading_files)
    if avg_uploading_files:
        message_files = f'\n'.join(list(uploading_files))
        for user in (await Users.all()):
            info_text = 'Новые файлы:' if avg_uploading_files > 1 else 'Новый файл:'
            try:
                await BOT.send_message(
                    chat_id=user.tg_id,
                    text=f'{info_text}\n\n{message_files}',
                )
            except:
                pass
