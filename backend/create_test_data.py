from django.contrib.auth import get_user_model
from events.models import Category, Event
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("Создание тестовых данных...")

# Создаем категории
categories = ['Технологии', 'Искусство', 'Образование', 'Спорт', 'Музыка']
for cat in categories:
    Category.objects.get_or_create(name=cat)
    print(f"Категория создана: {cat}")

# Создаем организатора
if not User.objects.filter(username='organizer').exists():
    organizer = User.objects.create_user(
        username='organizer',
        email='organizer@example.com',
        password='organizer123',
        first_name='Иван',
        last_name='Организаторов',
        role='organizer'
    )
    print('Организатор создан')

# Создаем обычного пользователя
if not User.objects.filter(username='user').exists():
    user = User.objects.create_user(
        username='user',
        email='user@example.com',
        password='user123',
        first_name='Петр',
        last_name='Пользователев',
        role='user'
    )
    print('Пользователь создан')

# Создаем тестовые мероприятия
if Event.objects.count() < 3:
    tech_category = Category.objects.get(name='Технологии')
    organizer = User.objects.get(username='organizer')
    
    events = [
        {
            'title': 'Конференция по AI и Machine Learning',
            'description': 'Крупнейшая конференция по искусственному интеллекту и машинному обучению в России',
            'date': timezone.now() + timedelta(days=10),
            'location': 'Москва, Digital October',
            'category': tech_category,
            'creator': organizer,
            'status': 'published',
            'max_participants': 500,
            'price': 2990
        },
        {
            'title': 'Воркшоп по Django для начинающих',
            'description': 'Практический воркшоп по созданию веб-приложений на Django',
            'date': timezone.now() + timedelta(days=5),
            'location': 'Онлайн',
            'category': tech_category,
            'creator': organizer,
            'status': 'published',
            'max_participants': 100,
            'price': 0
        },
    ]
    
    for event_data in events:
        Event.objects.create(**event_data)
    
    print('Тестовые мероприятия созданы')

print("Тестовые данные готовы!")
print("\nЛогины для тестирования:")
print("1. Админ: admin / admin123")
print("2. Организатор: organizer / organizer123")
print("3. Пользователь: user / user123")
