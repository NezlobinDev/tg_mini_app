import re


async def is_endswith(file_name, list_sw):
    """ Проверка на разрешение файла """
    for el in list_sw:
        if file_name.endswith(el):
            return el


async def format_filename(filename, station='MSC'):
    """ Приобразование имени файла
    ST1_15421_241210092208_8224L -> MSC_Stilsat1_20241210_092208_015421
    """
    sat_names = {
        'st1': 'Stilsat1',
    }
    if re.match(r'^ST1_\d{5}_\d{12}_\d{4}', filename):
        sat_name, orbit_id, timestamp, *_ = filename.split('_')
        sat_name = sat_names.get(sat_name.lower(), sat_name)
        timestamp = f'{timestamp[:6]}_{timestamp[6:]}'
        return f'{station}_{sat_name}_{timestamp}_0{orbit_id}'
    if re.match(r'^ST1_\d{2}_\d{6}_U\d{6}_\d{8}_[A-Z]+\d?_R\d$', filename):
        sat_name, *params = filename.split('_')
        sat_name = sat_names.get(sat_name.lower(), sat_name)
        return f'{station}_{sat_name}_' + '_'.join(params)
    return filename
