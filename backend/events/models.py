from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('cancelled', 'Отменено'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    date = models.DateTimeField(verbose_name='Дата и время')
    location = models.CharField(max_length=200, verbose_name='Место')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name='Изображение')
    max_participants = models.IntegerField(default=0, verbose_name='Макс. участников')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Создатель')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    def __str__(self):
        return self.title
    
    def is_available(self):
        return self.status == 'published'
    
    def can_cancel_registration(self):
        """Можно ли отменять регистрации на это мероприятие"""
        from django.utils import timezone
        # Можно отменять минимум за 24 часа до начала
        return self.date > timezone.now() + timezone.timedelta(hours=24)
    
    def confirmed_registrations_count(self):
        """Количество подтвержденных регистраций"""
        return self.registrations.filter(status='confirmed').count()
    
    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-date']

class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('refunded', 'Средства возвращены'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные при встрече'),
        ('card_mir', 'Картой МИР онлайн'),
        ('card_other', 'Другой картой онлайн'),
        ('not_selected', 'Не выбран'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='registrations'
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='Мероприятие',
        related_name='registrations'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Зарегистрирован')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус регистрации')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='not_selected', verbose_name='Способ оплаты')
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name='Отменено')
    cancellation_reason = models.TextField(blank=True, verbose_name='Причина отмены')
    
    class Meta:
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        unique_together = ('user', 'event')
    
    def __str__(self):
        return f'{self.user.username} - {self.event.title}'
    
    def can_cancel(self):
        """Можно ли отменить эту регистрацию"""
        if self.status in ['cancelled', 'refunded']:
            return False
        return self.event.can_cancel_registration()
    
    def get_refund_amount(self):
        """Сумма возврата (если применимо)"""
        if self.event.price > 0 and self.status == 'confirmed':
            # Для демо - возвращаем полную сумму
            # В реальности здесь может быть логика с комиссиями
            return self.event.price
        return 0

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращено'),
        ('refund_pending', 'Ожидает возврата'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card_mir', 'Карта МИР'),
        ('card_other', 'Другая карта'),
    ]
    
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='Регистрация'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='Статус оплаты')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID транзакции')
    refund_transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID возврата')
    bank_response = models.JSONField(default=dict, blank=True, verbose_name='Ответ банка')
    refund_response = models.JSONField(default=dict, blank=True, verbose_name='Ответ на возврат')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='Оплачено')
    refunded_at = models.DateTimeField(blank=True, null=True, verbose_name='Возвращено')
    
    def __str__(self):
        return f'Платеж #{self.id} - {self.amount} руб.'
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
    
    def can_refund(self):
        """Можно ли сделать возврат"""
        return self.status == 'completed' and self.status != 'refunded'
    
    def get_refund_amount(self):
        """Сумма возврата"""
        if self.can_refund():
            # Для демо - полный возврат
            # В реальности можно учесть комиссии и время до мероприятия
            return self.amount
        return 0
