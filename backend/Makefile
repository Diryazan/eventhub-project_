.PHONY: help build up down restart logs shell migrate collectstatic createsuperuser test clean

help:
	@echo "=== EventHub Docker Management ==="
	@echo ""
	@echo "Основные команды:"
	@echo "  make build    - Сборка Docker образов"
	@echo "  make up       - Запуск всех контейнеров"
	@echo "  make down     - Остановка контейнеров"
	@echo "  make restart  - Перезапуск контейнеров"
	@echo "  make logs     - Просмотр логов"
	@echo ""
	@echo "Управление Django:"
	@echo "  make shell    - Войти в контейнер Django"
	@echo "  make migrate  - Применить миграции"
	@echo "  make collectstatic - Собрать статические файлы"
	@echo "  make createsuperuser - Создать суперпользователя"
	@echo "  make test-data - Создать тестовые данные"
	@echo ""
	@echo "Утилиты:"
	@echo "  make clean    - Очистка Docker"
	@echo "  make status   - Показать статус"
	@echo "  make backup   - Создать бэкап базы"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec django bash

migrate:
	docker-compose exec django python manage.py migrate

collectstatic:
	docker-compose exec django python manage.py collectstatic --noinput

createsuperuser:
	docker-compose exec django python manage.py createsuperuser

test-data:
	docker-compose exec django python create_test_data.py

clean:
	docker-compose down -v
	docker system prune -f

status:
	docker-compose ps
	@echo ""
	@echo "Доступные адреса:"
	@echo "  • Django: http://localhost:8000"
	@echo "  • База данных: localhost:5432"
	@echo ""
	@echo "Логины для тестирования:"
	@echo "  • Админ: admin / admin123"
	@echo "  • Организатор: organizer / organizer123"
	@echo "  • Пользователь: user / user123"

backup:
	mkdir -p backups
	docker-compose exec postgres pg_dump -U eventhub_user eventhub > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Бэкап создан в backups/"
