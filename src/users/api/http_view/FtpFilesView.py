from users.models import UserFiles
from fastapi import Request
from fastapi import APIRouter
from ftp.models import ScanFiles
from fastapi.responses import JSONResponse
from datetime import datetime


ftp_router = APIRouter(prefix='/users/ftp', tags=['Users'])


@ftp_router.get('/list_files/')
async def get_list_files(request: Request, date_from: str, date_to: str):
    """ Регистрация нового пользователя """
    if not date_from or not date_to:
        date_to = datetime.now().date()
        date_from = date_to
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        date_from = datetime.strptime(date_from, '%Y-%m-%d')

    user = request.state.user
    date_from = datetime.combine(date_from, datetime.min.time())
    date_to = datetime.combine(date_to, datetime.max.time())

    files = await ScanFiles.filter(date_add__gte=date_from, date_add__lte=date_to)
    user_files = await UserFiles.filter(file__id__in=[file.id for file in files], user=user)

    result = []

    interacted_file_ids = {(await user_file.file.last()).id: user_file for user_file in user_files}

    statuses = {
        ScanFiles.Statuses.DOWNLOADING: 'paused',
        ScanFiles.Statuses.UPLOADING: 'downloaded',
        UserFiles.FileStatuses.DOWNLOADING: 'downloading',
        UserFiles.FileStatuses.DOWNLOADED: 'downloaded',
        UserFiles.FileStatuses.PAUSE: 'paused',
        UserFiles.FileStatuses.ERROR: 'paused',
    }

    for file in files:
        file_data = {
            'id': file.id,
            'status_text': file.status,
            'file_name': file.file_name,
            'status': statuses.get(file.status, 'paused'),
        }
        if file.id in interacted_file_ids:
            u_file = interacted_file_ids[file.id]
            file_data['file_name'] = u_file.file_name
            file_data['status'] = statuses.get(u_file.status, 'paused'),
            file_data['status_text'] = u_file.status
        result.append(file_data)
    return JSONResponse(result)
