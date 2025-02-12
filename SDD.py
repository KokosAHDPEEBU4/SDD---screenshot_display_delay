import os
import time
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, Text, Scrollbar, VERTICAL, END
from PIL import ImageGrab
import threading

# Настройка темы (светлая/тёмная)
def update_theme():
    if theme_switch.get():
        ctk.set_appearance_mode("Dark")  # Тёмная тема
    else:
        ctk.set_appearance_mode("Light")  # Светлая тема
    # Обновляем стили для текстового поля и скроллера в зависимости от темы
    log_text.configure(bg=ctk.ThemeManager.theme["frame_bg_color"], fg=ctk.ThemeManager.theme["text_color"])
    scrollbar.configure(bg=ctk.ThemeManager.theme["frame_bg_color"])
    scrollbar_through.configure(bg=ctk.ThemeManager.theme["frame_bg_color"])

# Функция для выбора папки
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

# Функция для запуска создания скриншотов
def start_screenshots():
    folder = folder_path.get()
    hours = hours_entry.get()
    minutes = minutes_entry.get()
    seconds = seconds_entry.get()

    if not folder:
        messagebox.showerror("Ошибка", "Выберите папку для сохранения скриншотов.")
        return

    # Преобразуем введённые значения в целые числа (если поле пустое, используем 0)
    try:
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0

        # Вычисляем общий интервал в секундах
        interval = hours * 3600 + minutes * 60 + seconds

        if interval <= 0:
            messagebox.showerror("Ошибка", "Интервал должен быть положительным числом.")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числа для интервала.")
        return

    # Запуск создания скриншотов в отдельном потоке
    global stop_thread
    stop_thread = False
    threading.Thread(target=take_screenshots, args=(folder, interval), daemon=True).start()
    start_button.configure(state="disabled")
    stop_button.configure(state="normal")

# Функция для остановки создания скриншотов
def stop_screenshots():
    global stop_thread
    stop_thread = True
    start_button.configure(state="normal")
    stop_button.configure(state="disabled")

# Функция для создания скриншотов
def take_screenshots(folder, interval):
    if not os.path.exists(folder):
        os.makedirs(folder)

    while not stop_thread:
        # Получаем текущее время и дату
        now = datetime.now()
        # Форматируем время и дату для имени файла (с дефисами)
        timestamp_file = now.strftime("%H-%M-%S %d.%m.%Y")
        # Форматируем время и дату для вывода в лог (с двоеточиями)
        timestamp_log = now.strftime("%H:%M:%S %d.%m.%Y")
        # Создаем имя файла
        file_name = f"screenshot_{timestamp_file}.png"
        file_path = os.path.join(folder, file_name)

        # Делаем скриншот и сохраняем его
        screenshot = ImageGrab.grab()
        screenshot.save(file_path)

        # Выводим сообщение в текстовое поле
        log_message = f"Скриншот сохранен {timestamp_log}\n"
        log_text.insert(END, log_message)
        log_text.see(END)  # Автоматическая прокрутка к последнему сообщению

        # Ждем заданный интервал
        time.sleep(interval)

# Создаем главное окно
root = ctk.CTk()
root.title("Скриншоты с интервалом")
root.geometry("700x500")

# Переменные для хранения пути к папке и интервала
folder_path = ctk.StringVar()
hours_entry = ctk.StringVar(value="0")  
minutes_entry = ctk.StringVar(value="0")  
seconds_entry = ctk.StringVar(value="5") 

# Элементы интерфейса
ctk.CTkLabel(root, text="Папка для сохранения:").grid(row=0, column=0, padx=10, pady=10)
ctk.CTkEntry(root, textvariable=folder_path, width=300, state="readonly").grid(row=0, column=1, padx=10, pady=10)
ctk.CTkButton(root, text="Выбрать папку", command=select_folder).grid(row=0, column=3, padx=10, pady=10)

# Поля для ввода интервала
ctk.CTkLabel(root, text="Часы:").grid(row=0, column=4, padx=5, pady=5)
ctk.CTkEntry(root, textvariable=hours_entry, width=50).grid(row=0, column=5, padx=5, pady=5)
ctk.CTkLabel(root, text="Минуты:").grid(row=1, column=4, padx=5, pady=5)
ctk.CTkEntry(root, textvariable=minutes_entry, width=50).grid(row=1, column=5, padx=5, pady=5)
ctk.CTkLabel(root, text="Секунды:").grid(row=2, column=4, padx=5, pady=5)
ctk.CTkEntry(root, textvariable=seconds_entry, width=50).grid(row=2, column=5, padx=5, pady=5)

# Кнопки старта и остановки
start_button = ctk.CTkButton(root, text="Старт", command=start_screenshots)
start_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

stop_button = ctk.CTkButton(root, text="Стоп", command=stop_screenshots, state="disabled")
stop_button.grid(row=2, column=3, padx=10, pady=10, sticky="e")

# Текстовое поле для вывода логов
log_text = Text(root, wrap="word", height=10, font=("Arial", 12))
log_text.grid(row=3, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")

# Полоса прокрутки для текстового поля
scrollbar = Scrollbar(root, orient=VERTICAL, command=log_text.yview)
scrollbar.grid(row=3, column=7, sticky="ns")
log_text.config(yscrollcommand=scrollbar.set)

# Полоса прокрутки внутри окна
scrollbar_through = ctk.CTkScrollbar(root, orientation=VERTICAL, command=log_text.yview)
scrollbar_through.grid(row=3, column=7, sticky="ns")
log_text.config(yscrollcommand=scrollbar_through.set)

# Настройка расширения строк и столбцов
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

# Добавляем чекбокс для переключения темы
theme_switch = ctk.BooleanVar(value=True)  # По умолчанию темная тема
theme_checkbox = ctk.CTkCheckBox(root, text="Темная тема", variable=theme_switch, onvalue=True, offvalue=False, command=update_theme)
theme_checkbox.grid(row=1, column=0, columnspan=1, padx=10, pady=10)

root.mainloop()
