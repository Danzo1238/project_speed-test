import speedtest, tkinter as tk
import threading, os
from tkinter import ttk
from PIL import Image, ImageTk

# --- Создание окна ---
window = tk.Tk()
window.title('Speed Test')
window.geometry('300x400')
window.resizable(False, False)

st = speedtest.Speedtest()

# --- Виджеты ---
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, 'image.png')
image = Image.open(image_path)
image = image.resize((300, 400), Image.LANCZOS)
bg_image = ImageTk.PhotoImage(image)

bg_label = tk.Label(window, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


result_label = tk.Label(
    window,
    text='Загрузка: ---\nВыгрузка: ---\nПинг: ---\n',
    font=('Arial', 15),
    anchor='w',
    justify='left'
)
result_label.place(x=45, y=50)



progress_label = ttk.Progressbar()
progress_label.place(x=50, y=150, width=150, height=30)

start_button = tk.Button(text='Start', width=10)
start_button.place(x=70, y=190, width=100, height=30)

# --- Функции ---

def speed():
    """Сбрасываем интерфейс и запускаем первый этап"""
    progress_label['value'] = 0
    result_label.config(text='Загрузка: ---\nВыгрузка: ---\nПинг: ---')
    start_button.config(state='disabled')
    threading.Thread(target=download_step).start()


def download_step():
    """Этап загрузки"""
    download = round(st.download() / 8 / 1_000_000, 2)
    window.after(0, lambda: update_result(download=download))
    window.after(0, lambda: animate_progress_to(33))
    threading.Thread(target=upload_step, args=(download,)).start()


def upload_step(download):
    """Этап выгрузки"""
    upload = round(st.upload() / 8 / 1_000_000, 2)
    window.after(0, lambda: update_result(download=download, upload=upload))
    window.after(0, lambda: animate_progress_to(66))
    threading.Thread(target=ping_step, args=(download, upload)).start()


def ping_step(download, upload):
    """Этап пинга"""
    server = st.get_best_server()
    ping = server['latency']
    window.after(0, lambda: update_result(download=download, upload=upload, ping=ping))
    window.after(0, lambda: animate_progress_to(100))
    window.after(0, lambda: start_button.config(state='normal'))


def animate_progress_to(target):
    """Плавная анимация прогресс-бара до заданного значения"""
    current = progress_label['value']
    step = 1 if target > current else -1

    def _animate():
        nonlocal current
        if current != target:
            current += step
            progress_label['value'] = current
            window.after(10, _animate)

    _animate()


def update_result(download=None, upload=None, ping=None):
    """Обновление текста с результатами"""
    text_lines = [
        f'Загрузка: {download} Mbs' if download is not None else 'Загрузка: ---',
        f'Выгрузка: {upload} Mbs' if upload is not None else 'Выгрузка: ---',
        f'Пинг: {round(ping, 2)} ms' if ping is not None else 'Пинг: ---'
    ]
    result_label.config(text='\n'.join(text_lines))


# --- Назначаем кнопку ---
start_button.config(command=speed)

# --- Запуск GUI ---
window.mainloop()

