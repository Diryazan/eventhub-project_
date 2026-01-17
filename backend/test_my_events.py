#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, Category, Registration
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=== Создание тестовых данных для проверки 'Мои мероприятия' ===")

# Получаем тестовых пользователей
try:
    admin = User.objects.get(username='admin')
    user = User.objects.get(username='user')
    organizer = User.objects.get(username='organizer')
    
    print(f"Найден пользователь admin: {admin.username}")
    print(f"Найден пользователь user: {user.username}")
    print(f"Найден пользователь organizer: {organizer.username}")
    
    # Создаем тестовую категорию
    category, created = Category.objects.get_or_create(name='Тестовая категория')
    if created:
        print(f"Создана категория: {category.name}")
    
    # Создаем тестовые мероприятия для организатора
    events_data = [
        {
            'title': 'Мероприятие организатора 1',
            'description': 'Тестовое мероприятие созданное организатором',
            'date': timezone.now() + timedelta(days=3),
            'location': 'Тестовое место 1',
            'category': category,
            'creator': organizer,
            'status': 'published',
            'max_participants': 20,
            'price': 500
        },
        {
            'title': 'Мероприятие организатора 2',
            'description': 'Второе тестовое мероприятие',
            'date': timezone.now() + timedelta(days=5),
            'location': 'Тестовое место 2',
            'category': category,
            'creator': organizer,
            'status': 'published',
            'max_participants': 0,
            'price': 0
        }
    ]
    
    for event_data in events_data:
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            defaults=event_data
        )
        if created:
            print(f"Создано мероприятие: {event.title}")
    
    # Регистрируем пользователя на мероприятие
    event = Event.objects.first()
    if event:
        registration, created = Registration.objects.get_or_create(
            user=user,
            event=event,
            defaults={
                'status': 'confirmed',
                'payment_method': 'card_mir'
            }
        )
        if created:
            print(f"Создана регистрация для {user.username} на {event.title}")
    
    # Проверяем метод confirmed_registrations_count
    print("\n=== Проверка метода confirmed_registrations_count ===")
    for event in Event.objects.all():
        print(f"Мероприятие: {event.title}")
        print(f"  Всего регистраций: {event.registrations.count()}")
        print(f"  Подтвержденных регистраций: {event.confirmed_registrations_count()}")
    
    print("\n=== URL для проверки ===")
    print("1. Войдите как 'user' (пароль: user123)")
    print("2. Перейдите: http://localhost:8000/my-events/")
    print("3. Должны отображаться:")
    print("   - Созданные мероприятия (если вы организатор)")
    print("   - Зарегистрированные мероприятия")
    print("   - Платежи (если есть)")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
