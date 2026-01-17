FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements-prod.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements-prod.txt

# Копируем код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p static media

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "eventhub.wsgi:application"]
