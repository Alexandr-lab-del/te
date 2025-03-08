# Используем базовый образ Python
FROM python:3.10-slim

# Обновляем систему и устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Python-зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект в рабочую директорию
COPY . .

# Определяем порт приложения
EXPOSE 8000

# Команда по умолчанию запускается Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "myproject.wsgi:application"]
