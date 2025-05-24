from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from users.models import UserFiles, Users
from ftp.models import ScanFiles
import asyncio
import os
from ftp.utils import format_filename
from tortoise import Tortoise
from app.settings.db import MODELS, TORTOISE_ORM
from ftp.utils.commands import download_file

ftp_ws_router = APIRouter(prefix='/ftp', tags=['Ftp'])


@ftp_ws_router.websocket('/files/info/')
async def ws_file_info(websocket: WebSocket):
    """ Каждую секунду получать данные о файлах(страница со списком файлов) """
    await websocket.accept()
    try:
        message = await websocket.receive_json()
        user_id = message.get('user_id')
        file_ids = message.get('file_ids')

        user = await Users.get_or_none(id=user_id)

        statuses = {
            ScanFiles.Statuses.DOWNLOADING: 'paused',
            ScanFiles.Statuses.UPLOADING: 'downloaded',
            UserFiles.FileStatuses.DOWNLOADING: 'downloading',
            UserFiles.FileStatuses.DOWNLOADED: 'downloaded',
            UserFiles.FileStatuses.PAUSE: 'paused',
            UserFiles.FileStatuses.ERROR: 'paused',
        }

        while True:
            files = await ScanFiles.filter(id__in=file_ids)
            user_files = await UserFiles.filter(file__id__in=[file.id for file in files], user=user)
            interacted_file_ids = {(await user_file.file.last()).id: user_file for user_file in user_files}

            result = []
            for file in files:
                file_data = {
                    'id': file.id,
                    'status_text': file.status,
                    'file_name': file.file_name,
                    'status': statuses.get(file.status, 'paused'),
                }
                if file.id in interacted_file_ids:
                    u_file = interacted_file_ids[file.id]
                    file_data['file_name'] = u_file.file_name,
                    file_data['status'] = statuses.get(u_file.status, 'paused'),
                    file_data['status_text'] = u_file.status
                result.append(file_data)

            await websocket.send_json({
                'data': result,
                'status_code': 200 if result else 404,
            })
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            'error': str(e),
            'status_code': 500,
        })
        await websocket.close()


@ftp_ws_router.websocket('/file/info/')
async def ws_file_info(websocket: WebSocket):
    """ Начать скачивание/обновление данных о файле в реал тайме """
    await websocket.accept()
    try:
        message = await websocket.receive_json()
        user_id = message.get('user_id')
        file_id = message.get('file_id')

        user = await Users.get_or_none(id=user_id)

        while True:
            await Tortoise.init(
                config=TORTOISE_ORM,
                modules={model.split('.')[0]: model for model in MODELS},
            )

            file = await ScanFiles.filter(id=file_id).last()
            if not file:
                await websocket.send_json({
                    'error': f'Файл id {file_id} не найден',
                    'status_code': 404,
                })
                await websocket.close()
                break

            if file.status == ScanFiles.Statuses.DOWNLOADING:
                await websocket.send_json({
                    'error': 'Файл еще не готов к скачиванию',
                    'status_code': 405,
                })
                await websocket.close()
                break

            u_file = await UserFiles.filter(user=user, file=file).last()
            if not u_file:
                station_name = (await file.station.last()).name
                try:
                    os.mkdir(f'{user.get_dir()}/{file.file_name}')
                except (FileExistsError, OSError):
                    pass
                temp_f_name = '_'.join(file.file_name.split('_')[1:])
                u_file = await UserFiles.create(
                    file_name=await format_filename(temp_f_name, station_name),
                    file=file,
                    user=user,
                    process_id=-1,
                    file_dir=f'{user.get_dir()}/{file.file_name}',
                    err_mess='',
                )

                asyncio.create_task(download_file(file.id, user.id))
            elif u_file and u_file.status == UserFiles.FileStatuses.DELETE:
                await u_file.delete()
                await websocket.close()
                break

            await websocket.send_json({
                'data': {
                    'id': file.id,
                    'scan_file_name': file.file_name,
                    'file_name': u_file.file_name,
                    'total_size': file.size,
                    'loaded_size': u_file.size,
                    'status': u_file.status,
                    'file_dir': u_file.file_dir,
                },
                'status_code': 200,
            })
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    except Exception:
        import traceback
        await websocket.send_json({
            'error': str(traceback.format_exc()),
            'status_code': 500,
        })
        await websocket.close()


