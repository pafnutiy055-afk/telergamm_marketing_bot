# Используем официальный легкий образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта внутрь контейнера
COPY . .

# Обновляем pip и устанавливаем зависимости
# --no-cache-dir уменьшает размер образа
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Команда запуска бота
CMD ["python", "main.py"]
