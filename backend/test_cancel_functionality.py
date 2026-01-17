#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, Registration, Category
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=== Тест функционала отмены регистрации ===")

# Получаем тестовых пользователей
try:
    user = User.objects.get(username='user')
    organizer = User.objects.get(username='organizer')
    
    # Создаем тестовое мероприятие
    category = Category.objects.first()
    if not category:
        category = Category.objects.create(name='Тестовая категория')
    
    event = Event.objects.create(
        title='Тестовое мероприятие для отмены',
        description='Тестирование функционала отмены регистрации',
        date=timezone.now() + timedelta(days=7),  # Через 7 дней
        location='Тестовое место',
        category=category,
        creator=organizer,
        status='published',
        max_participants=10,
        price=1000
    )
    
    print(f"Создано мероприятие: {event.title}")
    print(f"ID мероприятия: {event.id}")
    
    # Создаем регистрацию
    registration = Registration.objects.create(
        user=user,
        event=event,
        status='confirmed',
        payment_method='card_mir'
    )
    
    print(f"Создана регистрация: {registration.id}")
    print(f"Пользователь: {registration.user.username}")
    print(f"Мероприятие: {registration.event.title}")
    
    # Тестируем функционал отмены
    print(f"\n=== Тест can_cancel() ===")
    print(f"Можно отменить: {registration.can_cancel()}")
    print(f"Сумма возврата: {registration.get_refund_amount()} руб.")
    
    print(f"\n=== Тест event.can_cancel_registration() ===")
    print(f"Мероприятие позволяет отмену: {event.can_cancel_registration()}")
    
    print(f"\n=== Проверка URL ===")
    print(f"URL мероприятия: http://localhost:8000/events/{event.id}/")
    print(f"URL отмены регистрации: http://localhost:8000/events/registration/{registration.id}/cancel/")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
