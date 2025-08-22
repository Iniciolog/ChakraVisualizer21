const { app, BrowserWindow, Menu } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let streamlitProcess;

function createWindow() {
  // Создаем окно браузера
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    title: 'Kirlian Platform - Биорезонансная диагностика',
    show: false, // Не показываем окно до загрузки
    titleBarStyle: 'default',
    webSecurity: true
  });

  // Устанавливаем меню
  const template = [
    {
      label: 'Приложение',
      submenu: [
        {
          label: 'О программе',
          click: () => {
            require('electron').dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'О программе',
              message: 'Kirlian Platform v1.0.0',
              detail: 'Разработано в НИЦ Инициологии и трансперсональной психологии\n\nПлатформа для биорезонансной диагностики и анализа энергетических центров.'
            });
          }
        },
        { type: 'separator' },
        {
          label: 'Выход',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Вид',
      submenu: [
        { role: 'reload', label: 'Обновить' },
        { role: 'forceReload', label: 'Принудительно обновить' },
        { role: 'toggleDevTools', label: 'Инструменты разработчика' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Сбросить масштаб' },
        { role: 'zoomIn', label: 'Увеличить' },
        { role: 'zoomOut', label: 'Уменьшить' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Полноэкранный режим' }
      ]
    }
  ];

  if (process.platform === 'darwin') {
    template[0].label = 'Kirlian Platform';
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Запускаем Streamlit сервер
  startStreamlitServer();

  // Показываем loading экран
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));
  mainWindow.show();

  // Ждем запуска сервера и загружаем приложение
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:5000');
  }, 5000);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startStreamlitServer() {
  const projectRoot = path.join(__dirname, '..');
  
  // Определяем команду для запуска Streamlit
  const streamlitCmd = process.platform === 'win32' ? 'streamlit.exe' : 'streamlit';
  
  streamlitProcess = spawn('python', ['-m', 'streamlit', 'run', 'main.py', '--server.headless=true', '--server.port=5000'], {
    cwd: projectRoot,
    stdio: 'pipe'
  });

  streamlitProcess.stdout.on('data', (data) => {
    console.log(`Streamlit stdout: ${data}`);
  });

  streamlitProcess.stderr.on('data', (data) => {
    console.error(`Streamlit stderr: ${data}`);
  });

  streamlitProcess.on('close', (code) => {
    console.log(`Streamlit process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Останавливаем Streamlit процесс
  if (streamlitProcess) {
    streamlitProcess.kill();
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Останавливаем Streamlit процесс при выходе
  if (streamlitProcess) {
    streamlitProcess.kill();
  }
});