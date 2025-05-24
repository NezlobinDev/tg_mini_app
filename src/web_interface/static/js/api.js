function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}


function get_user_data(){
    /* Информация о авторизованном пользователе */
    return $.ajax({
        url: `${get_url()}/api/users/me/`,
        method: 'GET',
        headers: {
            'Authorization': getCookie('Authorization') 
        },
        success: function(data){},
        error: function(data){}
    })
}

function reg_user(tg_user_id){
    /* Регистрация польхзователя */
    return $.ajax({
        url: `${get_url()}/api/users/reg/`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            'tg_id': tg_user_id,
        }),
        success: function(data){},
        error: function(data){} 
    })
}

function send_secret_code(tg_user_id){
    /* ОТправить код авторизации пользователю в телеграм */
    return $.ajax({
        url: `${get_url()}/api/users/auth/get_code/?user_id=${tg_user_id}`,
        method: 'GET',
        success: function(data){},
        error: function(data){}
    })
}

// -- сервера сканекс

function list_stations(server_id){
    /* Список серверов */
    return $.ajax({
        url: `${get_url()}/api/ftp/list_stations`,
        method: 'GET',
        success: function(data){},
        error: function(data){}
    })
}

// -- скачивание файлов
function get_files(date_from='', date_to=''){
    /* Список файлов */
    return $.ajax({
        url: `${get_url()}/api/users/ftp/list_files/?date_from=${date_from}&date_to=${date_to}`,
        method: 'GET',
        success: function(data){},
        error: function(data){}
    })
}

function start_download_file(file_id, fi_socket){
    /* Начать скачивание файла */
    return $.ajax({
        url: `${get_url()}/api/ftp/start_download_file/?file_id=${file_id}`,
        method: 'GET',
        success: function(data){},
        error: function(data){
            alert(data.responseJSON.message)
        }
    })
}

function pause_download_file(file_id, fi_socket){
    /* Поставить на паузу */
    return $.ajax({
        url: `${get_url()}/api/ftp/pause_download_file/?file_id=${file_id}`,
        method: 'GET',
        success: function(data){},
        error: function(data){
            alert(data.responseJSON.message)
        }
    })
}

function stop_download_file(file_id){
    /* Прекратить скачивание */
    return $.ajax({
        url: `${get_url()}/api/ftp/clear_download_file/?file_id=${file_id}`,
        method: 'GET',
        success: function(data){
            send_err_msg('downloads', data.message)
        },
        error: function(data){
            alert(data.responseJSON.message)
        }
    })
}
