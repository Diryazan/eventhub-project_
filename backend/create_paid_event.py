#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, Category
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=== Создание платного мероприятия ===")

# Получаем организатора
organizer = User.objects.get(username='organizer')

# Создаем платное мероприятие
category = Category.objects.get(name='Технологии')

event = Event.objects.create(
    title='Платная конференция по Django',
    description='Продвинутая конференция по Django фреймворку',
    date=timezone.now() + timedelta(days=14),
    location='Москва, Крокус Сити Холл',
    category=category,
    creator=organizer,
    status='published',
    max_participants=200,
    price=2990  # 2990 рублей
)

print(f"✅ Платное мероприятие создано:")
print(f"   Название: {event.title}")
print(f"   Цена: {event.price} руб.")
print(f"   URL: http://localhost:8000/events/{event.id}/")
