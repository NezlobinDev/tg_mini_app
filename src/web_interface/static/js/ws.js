function ws_update_all_file_info(socket, user_id, file_ids){
    let updateInterval;


    socket.addEventListener('open', function (event) {
        // Отправляем начальные параметры (user_id и file_ids)
        const params = {
            user_id: user_id,
            file_ids: file_ids 
        };
        socket.send(JSON.stringify(params));

        // Запускаем интервал для обновления данных каждые 5000 мс (5 секунд)
        updateInterval = setInterval(() => {
            socket.send(JSON.stringify({ action: 'update' }));
        }, 5000);
    });

    // Обработчик получения сообщений от сервера
    socket.addEventListener('message', function (event) {
        const response = JSON.parse(event.data);
        if (response.error) {} 
        else if (response.data) {
            response.data.forEach(file => {
                const file_button = document.getElementById(`file_all_info_${file.id}`)
                file_button.innerHTML = `
                <span class="file-name">${file.file_name}</span>
                <span class="status ${file.status}">${file.status_text}</span>
                `
            });
         }
    });

    // Обработчик закрытия соединения
    socket.addEventListener('close', function (event) {
        clearInterval(updateInterval); // Очищаем интервал при закрытии соединения
    });

    // Обработчик ошибок
    socket.addEventListener('error', function (error) {});

}


function ws_update_file_info(socket, user_id, file_id){
    /* Обновление данных о файле */

    let updateInterval;

    // Обработчик события открытия соединения
    socket.addEventListener('open', function (event) {
        // Отправляем начальные параметры (user_id и file_id)
        const params = {
            user_id: user_id,
            file_id: file_id 
        };
        socket.send(JSON.stringify(params));

        // Запускаем интервал для обновления данных каждые 1000 мс (1 секунда)
        updateInterval = setInterval(() => {
            socket.send(JSON.stringify({ action: 'update' }));
        }, 1000);
    });

    // Обработчик получения сообщений от сервера
    socket.addEventListener('message', function (event) {
        const response = JSON.parse(event.data);
        if (response.error) {
            send_err_msg('downloads', response.error)
            // Здесь можно обработать ошибку, например, показать уведомление пользователю
        } else if (response.data) {

            // Обновляем данные на странице
            const data = response.data
            const scan_f_name = document.getElementById('scan_f_name').value
            const f_name = document.getElementById('f_name').value
            if(scan_f_name != data.scan_file_name || f_name != data.file_name){
                create_html_file_info(
                    data.scan_file_name, data.file_name, 
                    data.status, data.file_dir, false,
                    file_id=data.id,
                )
            }
        
            document.getElementById('f_status').textContent = data.status
            document.getElementById('f_dir').value = data.file_dir

            const progressBar = document.getElementById(`progress-bar`);
            const progressValue = document.getElementById(`f_progress`);

            let percentage = (data.loaded_size / data.total_size) * 100;
            progressBar.style.width = percentage + '%'; 
            progressValue.innerText = `${data.loaded_size}/${data.total_size}mb`;
        }
    });

   // Обработчик закрытия соединения
    socket.addEventListener('close', function (event) {
        console.info('Соединение закрыто:', event);
        clearInterval(updateInterval); // Очищаем интервал при закрытии соединения
    });

    // Обработчик ошибок
    socket.addEventListener('error', function (error) {
        console.error('Ошибка WebSocket:', error);
    });
}