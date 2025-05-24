from users.models import UserFiles
import os


async def task_upd_file_data():
    """ Обновление размера и статусов скачиваемых файлов """
    all_user_files = await UserFiles.all().prefetch_related('file', 'user')
    for user_file in all_user_files:
        dir_path = f'{user_file.user.get_dir()}/{user_file.file.file_name}'
        base_file_name = os.path.splitext(user_file.file_name)[0]

        total_size = 0
        for file_name in os.listdir(dir_path):
            if file_name.startswith(base_file_name):
                full_file_path = os.path.join(dir_path, file_name)
                if os.path.isfile(full_file_path):
                    total_size += round(os.path.getsize(full_file_path) / (1024 * 1024), 2)

        if total_size >= user_file.file.size:
            user_file.status = UserFiles.FileStatuses.DOWNLOADED
        user_file.size = total_size
        await user_file.save()
