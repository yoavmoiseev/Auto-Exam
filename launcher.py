"""
Exam System - Offline Standalone Launcher
Запускает локальный сервер и открывает браузер
Работает без интернета в локальной сети
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import webbrowser
import socket
import sys
import os
import threading
import time

class ExamSystemLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Exam System - Offline Server")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Предотвращаем случайное закрытие
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.server_process = None
        self.server_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Заголовок
        header = tk.Label(
            self.root, 
            text="🎓 Exam System - Offline Mode", 
            font=("Arial", 18, "bold"),
            bg="#667eea",
            fg="white",
            pady=15
        )
        header.pack(fill=tk.X)
        
        # Информационная панель
        info_frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # IP адрес
        self.ip_label = tk.Label(
            info_frame,
            text="IP адрес: Определяется...",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333"
        )
        self.ip_label.pack(pady=5)
        
        # Порт
        self.port_label = tk.Label(
            info_frame,
            text="Порт: 5001",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333"
        )
        self.port_label.pack(pady=5)
        
        # URL для подключения
        self.url_label = tk.Label(
            info_frame,
            text="URL: Ожидание запуска...",
            font=("Arial", 11),
            bg="white",
            fg="#0066cc",
            cursor="hand2"
        )
        self.url_label.pack(pady=10)
        self.url_label.bind("<Button-1>", self.copy_url)
        
        # Статус
        self.status_label = tk.Label(
            info_frame,
            text="● Сервер остановлен",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#cc0000"
        )
        self.status_label.pack(pady=10)
        
        # Лог
        log_label = tk.Label(
            info_frame,
            text="Лог сервера:",
            font=("Arial", 10),
            bg="white",
            anchor="w"
        )
        log_label.pack(fill=tk.X, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            info_frame,
            height=8,
            font=("Consolas", 9),
            bg="#f5f5f5",
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки
        button_frame = tk.Frame(self.root, bg="white")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ Запустить сервер",
            command=self.start_server,
            font=("Arial", 11, "bold"),
            bg="#28a745",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.start_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_button = tk.Button(
            button_frame,
            text="■ Остановить сервер",
            command=self.stop_server,
            font=("Arial", 11, "bold"),
            bg="#dc3545",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.browser_button = tk.Button(
            button_frame,
            text="🌐 Открыть в браузере",
            command=self.open_browser,
            font=("Arial", 11, "bold"),
            bg="#007bff",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            state=tk.DISABLED
        )
        self.browser_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Получаем IP при запуске
        self.update_ip_address()
        
    def get_local_ip(self):
        """Получить локальный IP адрес"""
        try:
            # Создаем UDP соединение (не отправляем данные)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def update_ip_address(self):
        """Обновить отображение IP адреса"""
        ip = self.get_local_ip()
        self.ip_label.config(text=f"IP адрес: {ip}")
        self.url_label.config(text=f"URL: http://{ip}:5001")
        self.current_url = f"http://{ip}:5001"
    
    def copy_url(self, event=None):
        """Копировать URL в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_url)
        self.log_message(f"✓ URL скопирован в буфер обмена: {self.current_url}")
        messagebox.showinfo("Успех", f"URL скопирован:\n{self.current_url}")
    
    def log_message(self, message):
        """Добавить сообщение в лог"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_server(self):
        """Запустить Flask сервер"""
        if self.server_running:
            return
        
        try:
            self.log_message("Запуск сервера...")
            
            # Путь к Python и app.py
            if getattr(sys, 'frozen', False):
                # Если запущено как EXE
                app_path = os.path.join(os.path.dirname(sys.executable), 'app.py')
                python_exe = sys.executable
            else:
                # Если запущено как скрипт
                app_path = os.path.join(os.path.dirname(__file__), 'app.py')
                python_exe = sys.executable
            
            # Запускаем Flask в отдельном процессе
            self.server_process = subprocess.Popen(
                [python_exe, app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.server_running = True
            self.status_label.config(text="● Сервер запущен", fg="#28a745")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.browser_button.config(state=tk.NORMAL)
            
            self.log_message("✓ Сервер успешно запущен!")
            self.log_message(f"✓ Доступен по адресу: {self.current_url}")
            self.log_message("✓ Передайте этот адрес ученикам для подключения")
            
            # Запускаем чтение логов в отдельном потоке
            threading.Thread(target=self.read_server_output, daemon=True).start()
            
            # Автоматически открываем браузер через 2 секунды
            self.root.after(2000, self.open_browser)
            
        except Exception as e:
            self.log_message(f"✗ Ошибка запуска: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось запустить сервер:\n{str(e)}")
            self.server_running = False
    
    def read_server_output(self):
        """Читать вывод сервера"""
        if not self.server_process:
            return
        
        try:
            for line in self.server_process.stdout:
                if line.strip():
                    self.log_message(line.strip())
        except:
            pass
    
    def stop_server(self):
        """Остановить Flask сервер"""
        if not self.server_running:
            return
        
        try:
            self.log_message("Остановка сервера...")
            
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            
            self.server_running = False
            self.status_label.config(text="● Сервер остановлен", fg="#cc0000")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browser_button.config(state=tk.DISABLED)
            
            self.log_message("✓ Сервер остановлен")
            
        except Exception as e:
            self.log_message(f"✗ Ошибка остановки: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка при остановке сервера:\n{str(e)}")
    
    def open_browser(self):
        """Открыть браузер"""
        try:
            webbrowser.open(self.current_url)
            self.log_message(f"✓ Браузер открыт: {self.current_url}")
        except Exception as e:
            self.log_message(f"✗ Не удалось открыть браузер: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось открыть браузер:\n{str(e)}")
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.server_running:
            result = messagebox.askyesno(
                "Подтверждение",
                "Сервер запущен!\n\nВы уверены, что хотите закрыть?\nЭто остановит доступ для всех пользователей."
            )
            if not result:
                return
            
            self.stop_server()
        
        self.root.destroy()
    
    def run(self):
        """Запустить приложение"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ExamSystemLauncher()
    app.run()
