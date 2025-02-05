import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue

# Настройка бэкенда для графиков
import matplotlib
matplotlib.use('TkAgg')  # Используем TkAgg для графиков

# Настройки записи
sample_rate = 44100  # Частота дискретизации
duration = 10  # Длительность анализа (в секундах)

# Очередь для передачи данных между потоками
data_queue = queue.Queue()

# Функция для обработки аудио данных
def audio_callback(indata, frames, time, status):
    data = indata[:, 0]

    # Анализируем частотный спектр
    frequencies_data = np.fft.rfftfreq(len(data), d=1/sample_rate)
    spectrum_data = np.abs(np.fft.rfft(data))

    # Отправляем данные в очередь для обновления графика в главном потоке
    data_queue.put((spectrum_data, frequencies_data))

# Функция для обновления графика
def update_plot(frame):
    if not data_queue.empty():
        spectrum_data, frequencies_data = data_queue.get()

        plt.cla()  # Очистка текущего графика
        plt.plot(frequencies_data, 20 * np.log10(spectrum_data))
        plt.title('Частотный спектр в реальном времени')
        plt.xlabel('Частота (Гц)')
        plt.ylabel('Уровень (дБ)')
        plt.xlim(0, 20000)
        plt.ylim(-120, 0)

    return plt.gca().lines

# Запуск потока записи и анализа
plt.ion()  # Включение интерактивного режима
fig, ax = plt.subplots(figsize=(12, 6))

# Настройка анимации
ani = animation.FuncAnimation(fig, update_plot, blit=False, interval=50)

# Запуск потока записи аудио
with sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate):
    print("Начат анализ в реальном времени. Нажмите Ctrl+C для остановки.")
    try:
        plt.show()
        while True:
            pass  # Ждем завершения
    except KeyboardInterrupt:
        print("Анализ остановлен.")
