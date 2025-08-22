// Preload script для безопасности Electron приложения
const { contextBridge, ipcRenderer } = require('electron');

// Определяем API, который будет доступен в renderer процессе
contextBridge.exposeInMainWorld('electronAPI', {
  // Функции для взаимодействия с главным процессом
  platform: process.platform,
  versions: process.versions
});

// Предотвращаем выполнение небезопасного кода
window.addEventListener('DOMContentLoaded', () => {
  console.log('Kirlian Platform Desktop App loaded');
});