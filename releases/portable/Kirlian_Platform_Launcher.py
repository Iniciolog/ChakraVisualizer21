#!/usr/bin/env python3
"""
Kirlian Platform Desktop Launcher
Запускает Streamlit приложение и открывает его в браузере
"""

import subprocess
import webbrowser
import time
import sys
import os
import socket
from pathlib import Path

def check_port(port):
    """Проверяет, свободен ли порт"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except OSError:
        return False

def find_free_port(start_port=8501):
    """Находит свободный порт начиная с указанного"""
    port = start_port
    while not check_port(port):
        port += 1
    return port

def launch_kirlian_platform():
    """Запускает Kirlian Platform"""
    print("🚀 Запуск Kirlian Platform...")
    
    # Определяем путь к проекту
    current_dir = Path(__file__).parent
    main_py = current_dir / "main.py"
    
    if not main_py.exists():
        print("❌ Файл main.py не найден!")
        print("Убедитесь, что все файлы проекта находятся в той же папке.")
        input("Нажмите Enter для выхода...")
        return
    
    # Проверяем Python зависимости
    try:
        import streamlit
        print("✅ Streamlit найден")
    except ImportError:
        print("❌ Streamlit не установлен!")
        print("Установите командой: pip install streamlit")
        input("Нажмите Enter для выхода...")
        return
    
    # Находим свободный порт
    port = find_free_port()
    print(f"🌐 Используем порт: {port}")
    
    # Запускаем Streamlit
    try:
        print("⏳ Запуск сервера...")
        
        # Создаем команду запуска
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(main_py),
            "--server.headless=true",
            f"--server.port={port}",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
            "--theme.base=dark"
        ]
        
        # Запускаем процесс
        process = subprocess.Popen(
            cmd, 
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска сервера
        print("⏱️ Ожидание запуска сервера...")
        time.sleep(5)
        
        # Проверяем, что процесс запустился
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("❌ Ошибка запуска сервера:")
            if stderr:
                print(stderr)
            if stdout:
                print(stdout)
            input("Нажмите Enter для выхода...")
            return
        
        # Открываем браузер
        url = f"http://localhost:{port}"
        print(f"🌍 Открываем браузер: {url}")
        webbrowser.open(url)
        
        print("\n✅ Kirlian Platform запущен!")
        print(f"🔗 URL: {url}")
        print("\n📋 Инструкции:")
        print("• Приложение открылось в вашем браузере")
        print("• Для остановки закройте это окно или нажмите Ctrl+C")
        print("• Не закрывайте это окно пока используете приложение")
        
        # Ждем завершения
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Остановка сервера...")
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
            print("✅ Сервер остановлен")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        launch_kirlian_platform()
    except KeyboardInterrupt:
        print("\n👋 Выход...")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")