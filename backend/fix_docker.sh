#!/bin/bash

echo "🔧 Исправление проблем с Docker на Mac"
echo "======================================"

echo "1. Закрываем Docker..."
killall Docker 2>/dev/null || true

echo "2. Запускаем Docker Desktop..."
open -a Docker

echo "3. Ждем 30 секунд..."
sleep 30

echo "4. Проверяем Docker..."
if docker ps > /dev/null 2>&1; then
    echo "✅ Docker работает!"
else
    echo "❌ Docker не запустился"
    echo "Попробуйте перезагрузить Mac: sudo reboot"
    exit 1
fi

echo "5. Исправляем docker-compose.yml..."
cd ~/Documents/eventhub-project/backend 2>/dev/null || cd .

cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: eventhub
      POSTGRES_USER: eventhub_user
      POSTGRES_PASSWORD: eventhub_password
    ports:
      - "5432:5432"

  django:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgres://eventhub_user:eventhub_password@postgres:5432/eventhub
    command: >
      sh -c "sleep 5 &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
DOCKEREOF

echo "6. Запускаем проект..."
docker-compose up --build
