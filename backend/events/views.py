from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import json
import uuid
from .models import Event, Category, Registration, Payment
from .forms import EventForm, RegistrationForm

def home_view(request):
    events = Event.objects.filter(status='published').order_by('-date')
    categories = Category.objects.all()
    
    # Фильтрация
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category_id:
        events = events.filter(category_id=category_id)
    
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'events': events,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query or '',
    }
    return render(request, 'events/home.html', context)

def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Проверяем права доступа
    if event.status != 'published':
        if not request.user.is_authenticated:
            messages.error(request, 'Это мероприятие недоступно для просмотра.')
            return redirect('home')
        if event.creator != request.user and not request.user.is_admin():
            messages.error(request, 'У вас нет доступа к этому мероприятию.')
            return redirect('home')
    
    is_registered = False
    registration = None
    payment = None
    can_cancel = False
    
    # Подсчет подтвержденных регистраций
    confirmed_registrations_count = event.registrations.filter(status='confirmed').count()
    
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(user=request.user, event=event)
            is_registered = True
            can_cancel = registration.can_cancel()
            
            # Получаем информацию об оплате, если есть
            if hasattr(registration, 'payment'):
                payment = registration.payment
        except Registration.DoesNotExist:
            pass
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'registration': registration,
        'payment': payment,
        'confirmed_registrations_count': confirmed_registrations_count,
        'can_cancel': can_cancel,
    }
    return render(request, 'events/detail.html', context)

@login_required
def create_event_view(request):
    if not request.user.is_organizer() and not request.user.is_admin():
        messages.error(request, 'Только организаторы могут создавать мероприятия.')
        return redirect('home')
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            
            # Убедимся, что статус установлен
            if not event.status:
                event.status = 'draft' if not request.user.is_admin() else 'published'
            
            event.save()
            messages.success(request, f'Мероприятие "{event.title}" успешно создано!')
            # Перенаправляем на созданное мероприятие
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    
    return render(request, 'events/create.html', {'form': form})

@login_required
def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.creator != request.user and not request.user.is_admin():
        messages.error(request, 'Вы не можете редактировать это мероприятие.')
        return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Мероприятие обновлено!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/edit.html', {'form': form, 'event': event})

@login_required
def register_for_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id, status='published')
    
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, 'Вы уже зарегистрированы на это мероприятие.')
        return redirect('event_detail', event_id=event_id)
    
    if event.max_participants > 0:
        current_registrations = Registration.objects.filter(event=event, status='confirmed').count()
        if current_registrations >= event.max_participants:
            messages.error(request, 'На это мероприятие больше нет мест.')
            return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.event = event
            registration.save()
            
            # Если мероприятие платное и выбран онлайн-способ оплаты
            if event.price > 0 and registration.payment_method in ['card_mir', 'card_other']:
                # Создаем запись о платеже
                payment = Payment.objects.create(
                    registration=registration,
                    amount=event.price,
                    payment_method=registration.payment_method,
                    status='pending'
                )
                messages.success(request, 'Регистрация успешна! Перейдите к оплате.')
                return redirect('process_payment', payment_id=payment.id)
            else:
                # Для бесплатных мероприятий или наличной оплаты
                registration.status = 'confirmed'
                registration.save()
                
                if event.price > 0 and registration.payment_method == 'cash':
                    messages.success(request, 'Регистрация успешна! Оплата будет произведена наличными при встрече.')
                else:
                    messages.success(request, 'Регистрация успешна!')
                
                return redirect('event_detail', event_id=event.id)
    else:
        form = RegistrationForm()
    
    return render(request, 'events/register.html', {
        'event': event,
        'form': form,
    })

def process_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Проверяем права доступа
    if payment.registration.user != request.user:
        messages.error(request, 'У вас нет доступа к этому платежу.')
        return redirect('home')
    
    # Если платеж уже обработан
    if payment.status in ['completed', 'processing']:
        messages.info(request, 'Этот платеж уже обработан.')
        return redirect('event_detail', event_id=payment.registration.event.id)
    
    if request.method == 'POST':
        # Имитация обработки платежа через банк
        action = request.POST.get('action')
        
        if action == 'pay':
            # Генерируем ID транзакции
            transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
            
            # Имитируем запрос к банку
            bank_response = {
                'transaction_id': transaction_id,
                'status': 'success',
                'timestamp': timezone.now().isoformat(),
                'amount': float(payment.amount),
                'currency': 'RUB',
                'method': payment.payment_method,
                'bank': 'Demo Bank MIR',
                'message': 'Платеж успешно обработан'
            }
            
            # Обновляем платеж
            payment.status = 'completed'
            payment.transaction_id = transaction_id
            payment.bank_response = bank_response
            payment.paid_at = timezone.now()
            payment.save()
            
            # Обновляем регистрацию
            registration = payment.registration
            registration.status = 'confirmed'
            registration.save()
            
            messages.success(request, '✅ Оплата прошла успешно! Ваша регистрация подтверждена.')
            return redirect('event_detail', event_id=payment.registration.event.id)
        
        elif action == 'cancel':
            payment.status = 'failed'
            payment.bank_response = {
                'status': 'cancelled',
                'message': 'Платеж отменен пользователем'
            }
            payment.save()
            messages.info(request, 'Платеж отменен.')
            return redirect('event_detail', event_id=payment.registration.event.id)
    
    context = {
        'payment': payment,
        'event': payment.registration.event,
    }
    return render(request, 'events/payment.html', context)

@login_required
def cancel_registration_view(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, user=request.user)
    
    # Проверяем, можно ли отменить регистрацию
    if not registration.can_cancel():
        messages.error(request, 'Невозможно отменить регистрацию. Слишком поздно для отмены.')
        return redirect('event_detail', event_id=registration.event.id)
    
    if request.method == 'POST':
        # Получаем причину отмены
        reason = request.POST.get('reason', '')
        
        # Обновляем регистрацию
        registration.status = 'cancelled'
        registration.cancellation_reason = reason
        registration.cancelled_at = timezone.now()
        registration.save()
        
        # Если была оплата, обрабатываем возврат
        if hasattr(registration, 'payment'):
            payment = registration.payment
            if payment.can_refund() and payment.payment_method != 'cash':
                # Имитируем возврат средств
                refund_id = f"REF{uuid.uuid4().hex[:12].upper()}"
                payment.status = 'refunded'
                payment.refund_transaction_id = refund_id
                payment.refunded_at = timezone.now()
                payment.refund_response = {
                    'refund_id': refund_id,
                    'status': 'success',
                    'amount': float(payment.amount),
                    'timestamp': timezone.now().isoformat(),
                    'message': 'Средства возвращены на карту'
                }
                payment.save()
                
                registration.status = 'refunded'
                registration.save()
                
                messages.success(request, f'✅ Регистрация отменена. {payment.amount} ₽ возвращены на вашу карту.')
            elif payment.payment_method == 'cash':
                messages.success(request, '✅ Регистрация отменена. Возврат наличных необходимо согласовать с организатором.')
            else:
                messages.success(request, '✅ Регистрация отменена.')
        else:
            messages.success(request, '✅ Регистрация отменена.')
        
        return redirect('event_detail', event_id=registration.event.id)
    
    # GET запрос - показываем форму подтверждения
    refund_amount = registration.get_refund_amount()
    
    context = {
        'registration': registration,
        'refund_amount': refund_amount,
    }
    return render(request, 'events/cancel_registration.html', context)

@login_required
def my_events_view(request):
    # Созданные пользователем мероприятия
    created_events = Event.objects.filter(creator=request.user)
    
    # Мероприятия, на которые пользователь зарегистрирован
    registered_events = Event.objects.filter(registrations__user=request.user).distinct()
    
    # Получаем платежи пользователя
    payments = Payment.objects.filter(registration__user=request.user).order_by('-created_at')
    
    context = {
        'created_events': created_events,
        'registered_events': registered_events,
        'payments': payments,
    }
    return render(request, 'events/my_events.html', context)

@login_required
def my_payments_view(request):
    # Получаем все платежи пользователя
    payments = Payment.objects.filter(registration__user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    return render(request, 'events/my_payments.html', context)
