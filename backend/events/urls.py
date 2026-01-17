from django.urls import path
from .views import (
    home_view, event_detail_view, create_event_view,
    edit_event_view, register_for_event_view, my_events_view,
    process_payment_view, my_payments_view, cancel_registration_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('events/<int:event_id>/', event_detail_view, name='event_detail'),
    path('events/create/', create_event_view, name='create_event'),
    path('events/<int:event_id>/edit/', edit_event_view, name='edit_event'),
    path('events/<int:event_id>/register/', register_for_event_view, name='register_for_event'),
    path('events/registration/<int:registration_id>/cancel/', cancel_registration_view, name='cancel_registration'),
    path('payments/<int:payment_id>/', process_payment_view, name='process_payment'),
    path('my-events/', my_events_view, name='my_events'),
    path('my-payments/', my_payments_view, name='my_payments'),
]
