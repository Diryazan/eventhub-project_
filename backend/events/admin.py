from django.contrib import admin
from .models import Category, Event, Registration, Payment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'category', 'creator', 'status', 'price')
    list_filter = ('status', 'category', 'date')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'payment_method', 'created_at', 'cancelled_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('created_at', 'cancelled_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'registration', 'amount', 'payment_method', 'status', 'created_at', 'refunded_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('registration__user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'paid_at', 'refunded_at')
    
    actions = ['mark_as_completed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', paid_at=timezone.now())
        self.message_user(request, f"{queryset.count()} платежей отмечены как оплаченные")
    
    mark_as_completed.short_description = "Отметить как оплаченные"
    
    def mark_as_refunded(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='refunded', refunded_at=timezone.now())
        self.message_user(request, f"{queryset.count()} платежей отмечены как возвращенные")
    
    mark_as_refunded.short_description = "Отметить как возвращенные"
