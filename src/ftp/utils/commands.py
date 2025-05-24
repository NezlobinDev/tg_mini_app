import asyncio
import time

from ftp.models import ScanStations, ScanFiles
from collections import defaultdict
from datetime import datetime
from users.models import UserFiles, Users
from tortoise import Tortoise
from app.settings.db import TORTOISE_ORM, MODELS


async def get_cmd(key_cmd, station_name, **kwargs):
    """ Получить команду """
    data = {}

    def read_file(file_path):
        """ Вытаскиваем команды из файла """
        with open(file_path, 'r') as f:
            return f.read().replace('\n', '').split('###')

    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, read_file, 'ftp/utils/ssh_commands.txt')
    station = await ScanStations.get(name=station_name)
    replace_params = {
        'FTP_PWD': station.pwd,
        'FTP_USER': station.login,
        'FTP_URL': station.station_url,
        'SET_SSL': '',
        'LS': f'ls {station.patch};' if station.patch else 'ls;',
    }
    if station.is_ssl:
        replace_params.update({
            'SET_SSL': 'set ftp:ssl-force true; '
                       'set ftp:ssl-protect-data true; '
                       'set ftp:ssl-allow true; '
                       'set ssl:verify-certificate no;',
        })

    for el in res:
        name, command = el.split(' -cmd ')
        data.update({name: command})
    for key, value in replace_params.items():
        data[key_cmd] = data[key_cmd].replace(key, value)
    cmd = data[key_cmd]
    if key_cmd != 'files_ftp':
        cmd = data[key_cmd].format_map(defaultdict(lambda: '', **kwargs))
    return cmd


async def run_command(command):
    """ Запуск асинхронного сопроцесса """
    process = await asyncio.create_subprocess_exec(
        *['/bin/bash', '-c', command],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    return stdout.decode('utf-8').strip(), stderr.decode().strip(), process.returncode


async def list_files_ftp():
    """
    Запрос к ftp scannex на получение списка файлов

    результат:
    {
        'MSK_ST1_01_014932_U114154_20241108_RUMA1_R0': {
            'date': datetime.datetime(2025, 11, 8, 0, 0),
            'station': <ScanStations: 3>,
            'name': 'MSK_ST1_01_014932_U114154_20241108_RUMA1_R0',
            'size': 16656.09,
            'permits': {'log', 'dat', 'dat.md5'},
        },
        ...
    }
    """
    files = {}
    stations = await ScanStations.all()
    for station in stations:
        stdout, stderr, returncode = await run_command(
            await get_cmd('files_ftp', station.name),
        )
        if returncode != 0:
            continue

        for line in stdout.splitlines():
            split_data = line.split()
            if len(split_data) < 5:
                continue

            year, size, month, day, file_name = split_data
            if len(file_name.split('.', 1)) < 2:
                continue

            size = round(int(size) / (1024 * 1024), 2)
            file_date = datetime.strptime(f'{year} {month} {day}', '%Y %b %d')
            f_name, f_permit = file_name.split('.', 1)
            if not files.get(f_name):
                files.update({
                    f_name: {
                        'date': file_date,
                        'station': station,
                        'name': f'{station.name.upper()}_{f_name}',
                        'size': size,
                        'permits': {f_permit},
                    },
                })
            else:
                files[f_name]['permits'].add(f_permit)
                files[f_name]['size'] += size

    return files


async def get_remote_file_size(file_data):
    """ Функция для получения размера файла на сервере scanex """
    stdout, stderr, returncode = run_command(
        get_cmd(
            'file_size_scanex',
            file_data['station'].name,
            file_name=f"{file_data['name']}.*",
        )
    )
    if returncode != 0:
        return 0
    return int(stdout.split('\t')[0])


async def pause_download(u_file):
    """ Поставить на паузу """
    station = (await (await u_file.file.last()).station).name
    cmd_pause = await get_cmd('pause_download', station, pid=u_file.process_id)
    await run_command(cmd_pause)
    u_file.status = UserFiles.FileStatuses.PAUSE
    await u_file.save()


async def unpause_download(u_file):
    """ Снять с паузы """
    station = (await (await u_file.file.last()).station).name
    cmd_unpause = await get_cmd('play_download', station, pid=u_file.process_id)
    await run_command(cmd_unpause)
    u_file.status = UserFiles.FileStatuses.DOWNLOADING
    await u_file.save()


async def stop_download(u_file):
    """ Остановить загрузку и удалить данные """
    station = (await (await u_file.file.last()).station).name
    cmd_clear_process = await get_cmd('stop_download', station, pid=u_file.process_id)
    cmd_clear_dir = await get_cmd('clear_download', station)
    await run_command(cmd_clear_process)
    await run_command(cmd_clear_dir)

    u_file.status = UserFiles.FileStatuses.DELETE
    await u_file.save()


async def download_file(file_id, user_id):
    """ Начать скачивание файла """

    async def t_init():
        """ tortoise init """
        return await Tortoise.init(
            config=TORTOISE_ORM,
            modules={model.split('.')[0]: model for model in MODELS},
        )
    await t_init()

    user = await Users.get(id=user_id)
    file = await ScanFiles.get(id=file_id)
    file_permits = [] if not file.permits else file.permits.split('|')

    for permit in file_permits:
        await t_init()

        file = await ScanFiles.get(id=file.id)
        u_file = await UserFiles.get(file__id=file.id)
        station = (await file.station.last())

        cmd = await get_cmd(
            'download',
            station_name=station.name,
            scan_dir=f'{station.patch}/',
            file_name=file.file_name,
            new_file_name=u_file.file_name,
            download_path=f'{user.get_dir()}/{file.file_name}',
            permit_scan=permit,
            permit=permit.replace('raw', 'dat'),
            filename='{filename}',
        )
        try:
            stdout, stderr, returncode = await run_command(cmd)

            if returncode != 0:
                u_file.status = UserFiles.FileStatuses.ERROR
                u_file.err_mess = stderr
                return await u_file.save()

            process_id = str(stdout).replace('\n', '')
            process_id = int(process_id) if process_id.isdigit() else 0
            if process_id:
                u_file.process_id = process_id
                await u_file.save()

        except Exception as _e:
            u_file.status = UserFiles.FileStatuses.ERROR
            u_file.err_mess = str(_e)
            return await u_file.save()
