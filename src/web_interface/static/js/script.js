function hideLoading() {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('loading_mess').style.display = 'none';
}

function waitForTelegramWebApp() {
  return new Promise((resolve) => {

    document.getElementById('loading').style.display = 'flex';
    let loading_mess = document.getElementById('loading_mess')
    loading_mess.style.display = 'flex'
    loading_mess.innerHTML = 'Загружаю клиента..'
    const checkTelegramWebApp = setInterval(() => {
      let tg_user = window.Telegram.WebApp.initDataUnsafe.user
      if(!tg_user){
        tg_user = {'id': 683152578}
      }
     /* 
     Раскоментировать при деплое после тестирования и поднятия wss & https
     if (window.Telegram.WebApp.initDataUnsafe.user) {
        clearInterval(checkTelegramWebApp);
        hideLoading(); // Скрываем анимацию загрузки
        resolve();
      }*/
      
      // Автоизация/Регистрация пользователя
      get_user_data().catch(err => {
        if(err.status == 401){
          loading_mess.innerHTML = 'Запрос авторизации...'
          send_secret_code(tg_user.id).catch(err1 => {
            if(err1.status == 404){
              loading_mess.innerHTML = 'Клиент не  найден, регистрирую.'
                reg_user(tg_user.id).then(resp => {
                  loading_mess.innerHTML = 'Кнопка авторизации отправлена в телеграм..'
                  send_secret_code(tg_user.id);
                  clearInterval(checkTelegramWebApp);
                  resolve();
                });
            }
          }).then(resp => {
            loading_mess.innerHTML = 'Кнопка авторизации отправлена в телеграм..'
            clearInterval(checkTelegramWebApp);
            resolve();
          })
        }
        
        if(err.status == 405){
            loading_mess.innerHTML = 'Отказано в доступе'
            clearInterval(checkTelegramWebApp);
            resolve();
        }
      }).then(resp => {
        if(resp){
          loading_mess.innerHTML = 'Загрузка webapp...'
          document.getElementById('content').style.display = 'block';
          clearInterval(checkTelegramWebApp);
          hideLoading();
          resolve();
        }
      })

    }, 1000); // Проверяем каждые 1000 миллисекунд
  });
}

waitForTelegramWebApp().then(() => {
  // Показываем содержимое страницы после загрузки Telegram Web App
  getUserData();
});

function getScanServers(){
  /* Сервера сканекса */
  list_stations().then(data => {
    const group_list = document.getElementById('groupList')
    group_list.innerHTML = ''
    data.forEach((s_name) => {
      group_list.innerHTML +=  `<li>${s_name}</li>`
    })
  })
}


function getUserData() {
  /*const user = window.Telegram.WebApp.initDataUnsafe.user
  document.getElementById('userName').textContent = `${user.first_name} ${user.last_name}`
  document.getElementById('userId').textContent = `${user.id}`*/

  get_user_data().then(user => {
    document.getElementById('userId').innerHTML = user['tg_id']
    document.getElementById('avg_download').innerHTML = user['avg_download']
    if(user['is_admin']){
      document.getElementById('user_status').classList.add('admin')
      document.getElementById('user_status').innerHTML = 'Администратор'
    }
    else{
      document.getElementById('user_status').classList.add('user')
      document.getElementById('user_status').innerHTML = 'Пользователь'
    }
  })

}

function getFiles(date_from='', date_to='') {

  const listfiles = document.getElementById('fileList')
  listfiles.innerHTML = ''
  
  get_files(date_from, date_to).then(resp => {
    view_file_ids = []
    resp.forEach((file) => {
      view_file_ids.push(file.id)
      listfiles.innerHTML += `
        <button class="clickable-file" onclick="file_info(${file.id})" id="file_all_info_${file.id}">
            <span class="file-name">${file.file_name}</span>
            <span class="status ${file.status}">${file.status_text}</span>
        </button>
      `
    })

    if(view_file_ids){
      get_user_data().then(user => {
        file_all_info_socket = new WebSocket(`ws://${get_url('ws')}/ws/ftp/files/info/`);
        ws_update_all_file_info(file_all_info_socket, user.id, view_file_ids);
      });
    }

  })

}


// обработка нажатия на файл
function file_info(file_id) {
  get_user_data().then(user => {
    showPage('file_info')
    create_html_file_info()
    ws_update_file_info(file_info_socket, user.id, file_id)
  })
}

// обработка ошибок выбора дат
document.addEventListener('DOMContentLoaded', function() {
  const startDateInput = document.getElementById('start-date');
  const endDateInput = document.getElementById('end-date');
  
  const today = new Date().toISOString().split('T')[0];
  startDateInput.value = today;
  endDateInput.value = today;
  
  function validateDates() {
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);
    
    if (endDate < startDate) {
      startDateInput.classList.add('error');
      endDateInput.classList.add('error');
    } else {

      showPage('downloads')
      if(file_all_info_socket){ file_all_info_socket.close(); }


      startDateInput.classList.remove('error');
      endDateInput.classList.remove('error');
    }
  }
  
  startDateInput.addEventListener('change', validateDates);
  endDateInput.addEventListener('change', validateDates);
});