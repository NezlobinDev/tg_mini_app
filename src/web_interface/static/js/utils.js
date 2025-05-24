let file_info_socket;
let file_all_info_socket;
let view_file_ids = [];

function get_url(prodocol='') {
    const url = new URL(window.location.href);
    if(prodocol === 'ws')
        return url.host
    return `${url.protocol}//${url.host}`
}

function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
      page.classList.remove('active');
    });
    if (pageId === 'profile') { getUserData(); }
    if (pageId === 'servers') { getScanServers() }
  
  
    // когда пользователь на странице со списком файлов
    if (pageId === 'downloads') {
      const startDateInput = document.getElementById('start-date');
      const endDateInput = document.getElementById('end-date');
      getFiles(startDateInput.value, endDateInput.value);
    }
    if (pageId != 'downloads' && file_all_info_socket){ file_all_info_socket.close(); }
  
    // когда пользователь на странице с информацией о файле
    if (pageId === 'file_info'){
      file_info_socket = new WebSocket(`ws://${get_url('ws')}/ws/ftp/file/info/`);
    }
    if (pageId != 'file_info' && file_info_socket){ file_info_socket.close(); }
  
    document.getElementById(pageId).classList.add('active');
  }

function send_err_msg(pageId, message){
    showPage(pageId)
    alert(message)
}

function create_html_file_info(
    scan_f_name='unknown',
    f_name='unknown',
    f_status='Не доступен для скачивания',
    f_dir='unknown',
    disabled_btn=true,
    file_id=-1,

){
    const fileinfo = document.getElementById('file_info')
    fileinfo.innerHTML = `
    <h3>Информация о файле</h3><hr>
    <div class="info-item">
        <span class="label">Сканекс:</span>
        <input class="value" id="scan_f_name" value="${scan_f_name}" disabled></input>
    </div>

    <div class="info-item">
        <span class="label">Название:</span>
        <input class="value" id="f_name" value="${f_name}" disabled></input>
    </div>

    <div class="info-item">
        <span class="label">Статус:</span>
        <span class="value" id="f_status">${f_status}</span>
    </div>

    <div class="info-item">
        <span class="label">Размер:</span>
        <span class="value" id="f_progress">0/0mb</span>
    </div>

    <div class="info-item">
        <span class="label">Директория:</span>
        <input class="value" id="f_dir" value="${f_dir}" disabled></input>
    </div>

    <div class="info-item">
        <div class="progress-container">
            <div class="progress-bar" id="progress-bar">
            </div>
        </div>
    </div>
    `

    if (!disabled_btn) {
       fileinfo.innerHTML += `
       <div class="info-item">
            <button class="custom_button" onclick="pause_download_file(${file_id})">⏸️</button>
            <button class="custom_button" onclick="start_download_file(${file_id})">▶️</button>
            <button class="custom_button" onclick="stop_download_file(${file_id})">⏹️</button>
        </div>
       `
    }

}