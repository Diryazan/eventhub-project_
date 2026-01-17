#!/bin/bash

echo "🎉 Запуск EventHub на Mac"
echo "========================"

# Проверяем, запущен ли Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker не запущен"
    echo "Запустите Docker Desktop и попробуйте снова"
    open -a Docker
    echo "⏳ Ожидаю запуск Docker..."
    sleep 10
fi

# Строим образы если нужно
if [ "$1" = "--build" ]; then
    echo "🔨 Сборка Docker образов..."
    docker-compose build
fi

# Запускаем контейнеры
echo "🐳 Запуск контейнеров..."
docker-compose up -d

# Ждем пока все поднимется
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Показываем статус
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "✅ EventHub запущен!"
echo ""
echo "🌐 Доступные адреса:"
echo "   • Главная страница: http://localhost"
echo "   • Админка: http://localhost/admin"
echo "   • База данных (Adminer): http://localhost:8080"
echo ""
echo "👤 Тестовые пользователи:"
echo "   • Админ: admin / admin123"
echo "   • Организатор: organizer / organizer123"
echo "   • Пользователь: user / user123"
echo ""
echo "📝 Логи: docker-compose logs -f"
echo "🛑 Остановка: docker-compose down"
