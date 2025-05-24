from fastapi import APIRouter, Request
from ftp.models import ScanStations
from fastapi.responses import JSONResponse
from ftp.utils.commands import pause_download, unpause_download, stop_download
from users.models import UserFiles


ftp_router = APIRouter(prefix='/ftp', tags=['Ftp'])


@ftp_router.get('/list_stations')
async def get_list_stations(request: Request):
    """ Список серверов сканекса """
    stations = await ScanStations.all()
    return JSONResponse([station.name for station in stations])


@ftp_router.get('/pause_download_file/')
async def pause_download_file(request: Request, file_id: int):
    """ Приостановить скачивание файла """
    file = await UserFiles.filter(file__id=file_id).last()
    if request.state.user != (await file.user.last()):
        return JSONResponse(
            {'message': 'Файл вам не принадлежит'},
            status_code=405,
        )
    if not file:
        return JSONResponse(
            {'message': 'Файл не найден'},
            status_code=404,
        )
    for f_status in [UserFiles.FileStatuses.PAUSE, UserFiles.FileStatuses.DELETE]:
        if file.status == f_status:
            return JSONResponse(
                {'message': f'Файл в статусе: {f_status}'},
                status_code=404,
            )
    if file.status == UserFiles.FileStatuses.DOWNLOADED:
        return JSONResponse(
            {'message': 'Файл уже скачен'},
            status_code=405,
        )
    if file.status == UserFiles.FileStatuses.ERROR:
        return JSONResponse(
            {'message': f'При скачивании возникла ошибка: {file.err_mess}'},
            status_code=405,
        )
    await pause_download(file)
    return JSONResponse({'message': 'ok'}, status_code=200)


@ftp_router.get('/start_download_file/')
async def start_download_file(request: Request, file_id: int):
    """ Возвобновить скачивание файла """
    file = await UserFiles.filter(file__id=file_id).last()
    if request.state.user != (await file.user.last()):
        return JSONResponse(
            {'message': 'Файл вам не принадлежит'},
            status_code=405,
        )
    if not file:
        return JSONResponse(
            {'message': 'Файл не найден'},
            status_code=404,
        )
    for f_status in [UserFiles.FileStatuses.DOWNLOADING, UserFiles.FileStatuses.DELETE]:
        if file.status == f_status:
            return JSONResponse(
                {'message': f'Файл в статусе: {f_status}'},
                status_code=404,
            )
    if file.status == UserFiles.FileStatuses.DOWNLOADED:
        return JSONResponse(
            {'message': 'Файл уже скачен'},
            status_code=404,
        )
    if file.status == UserFiles.FileStatuses.ERROR:
        return JSONResponse(
            {'message': f'При скачивании возникла ошибка: {file.err_mess}'},
            status_code=405,
        )
    await unpause_download(file)
    return JSONResponse({'message': 'ok'}, status_code=200)


@ftp_router.get('/clear_download_file/')
async def clear_download_file(request: Request, file_id: int):
    """ Остановить скачивание файла и очистить данные """
    file = await UserFiles.filter(file__id=file_id).last()
    if request.state.user != (await file.user.last()):
        return JSONResponse(
            {'message': 'Файл вам не принадлежит'},
            status_code=405,
        )
    if not file:
        return JSONResponse(
            {'message': 'файл не найден'},
            status_code=404,
        )
    await stop_download(file)
    return JSONResponse({'message': 'Данные о файле очищены'})
