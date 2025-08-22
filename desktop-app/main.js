const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const net = require('net');

let mainWindow;
let streamlitProcess;
const STREAMLIT_PORT = 8501;

// Функция проверки доступности порта
function checkPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.once('close', () => resolve(true));
      server.close();
    });
    server.on('error', () => resolve(false));
  });
}

// Функция поиска свободного порта
async function findFreePort(startPort) {
  let port = startPort;
  while (!(await checkPort(port))) {
    port++;
  }
  return port;
}

function createWindow() {
  // Создаем окно браузера
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: false // Для локального сервера
    },
    title: 'Kirlian Platform - Биорезонансная диагностика',
    show: false,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    frame: true,
    resizable: true
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

async function startStreamlitServer() {
  return new Promise(async (resolve, reject) => {
    try {
      // Определяем путь к проекту
      const projectRoot = path.join(__dirname, '..');
      const mainPyPath = path.join(projectRoot, 'main.py');
      
      // Проверяем существование main.py
      if (!fs.existsSync(mainPyPath)) {
        throw new Error(`main.py не найден по пути: ${mainPyPath}`);
      }
      
      // Находим свободный порт
      const port = await findFreePort(STREAMLIT_PORT);
      console.log(`Запускаем Streamlit на порту ${port}`);
      
      // Определяем команду для запуска
      const pythonCmd = process.platform === 'win32' ? 'python.exe' : 'python3';
      const args = [
        '-m', 'streamlit', 'run', 'main.py',
        '--server.headless=true',
        `--server.port=${port}`,
        '--server.address=localhost',
        '--browser.gatherUsageStats=false',
        '--theme.base=dark'
      ];
      
      console.log(`Команда запуска: ${pythonCmd} ${args.join(' ')}`);
      
      streamlitProcess = spawn(pythonCmd, args, {
        cwd: projectRoot,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });

      let serverReady = false;
      
      streamlitProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`Streamlit: ${output}`);
        
        // Проверяем готовность сервера
        if (output.includes('You can now view') || output.includes('Local URL')) {
          serverReady = true;
          console.log('Streamlit сервер готов!');
          resolve(port);
        }
      });

      streamlitProcess.stderr.on('data', (data) => {
        const error = data.toString();
        console.error(`Streamlit error: ${error}`);
        
        // Некоторые сообщения в stderr не критичны
        if (!error.includes('WARNING') && !serverReady) {
          reject(new Error(`Ошибка запуска Streamlit: ${error}`));
        }
      });

      streamlitProcess.on('close', (code) => {
        console.log(`Streamlit процесс завершен с кодом ${code}`);
        if (!serverReady && code !== 0) {
          reject(new Error(`Streamlit завершился с ошибкой, код: ${code}`));
        }
      });

      streamlitProcess.on('error', (error) => {
        console.error('Ошибка при запуске Streamlit:', error);
        reject(error);
      });

      // Таймаут для запуска
      setTimeout(() => {
        if (!serverReady) {
          reject(new Error('Таймаут запуска Streamlit сервера'));
        }
      }, 30000); // 30 секунд
      
    } catch (error) {
      reject(error);
    }
  });
}

app.whenReady().then(async () => {
  try {
    console.log('Запуск приложения...');
    await initializeApp();
  } catch (error) {
    console.error('Ошибка инициализации:', error);
    dialog.showErrorBox('Ошибка запуска', `Не удалось запустить приложение: ${error.message}`);
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      initializeApp();
    }
  });
});

async function initializeApp() {
  createWindow();
  
  // Показываем loading экран
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));
  mainWindow.show();
  
  try {
    // Запускаем Streamlit сервер
    const port = await startStreamlitServer();
    
    // Ждем немного и загружаем приложение
    setTimeout(() => {
      mainWindow.loadURL(`http://localhost:${port}`);
      console.log(`Приложение загружено на http://localhost:${port}`);
    }, 2000);
    
  } catch (error) {
    console.error('Ошибка запуска Streamlit:', error);
    
    // Показываем страницу ошибки
    const errorHtml = `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ошибка запуска</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #0E0E20; color: #E0E0E0; }
            .error { background: #ff6b6b; padding: 20px; border-radius: 8px; margin: 20px; }
            .retry { background: #7A6EBF; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Ошибка запуска Kirlian Platform</h1>
        <div class="error">
            <p><strong>Причина:</strong> ${error.message}</p>
        </div>
        <p>Возможные решения:</p>
        <ul style="text-align: left; max-width: 500px; margin: 0 auto;">
            <li>Убедитесь, что Python установлен</li>
            <li>Проверьте, что установлен Streamlit: <code>pip install streamlit</code></li>
            <li>Перезапустите приложение</li>
        </ul>
        <br>
        <button class="retry" onclick="location.reload()">Попробовать снова</button>
    </body>
    </html>`;
    
    mainWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(errorHtml));
  }
}

app.on('window-all-closed', () => {
  // Останавливаем Streamlit процесс
  if (streamlitProcess) {
    console.log('Остановка Streamlit процесса...');
    streamlitProcess.kill('SIGTERM');
    
    // Принудительная остановка через 5 секунд
    setTimeout(() => {
      if (streamlitProcess && !streamlitProcess.killed) {
        streamlitProcess.kill('SIGKILL');
      }
    }, 5000);
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Останавливаем Streamlit процесс при выходе
  if (streamlitProcess) {
    streamlitProcess.kill('SIGTERM');
  }
});