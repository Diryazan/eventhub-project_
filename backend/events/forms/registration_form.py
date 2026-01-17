from django import forms
from ..models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Сортируем методы оплаты по удобству
        self.fields['payment_method'].choices = [
            ('cash', '💵 Наличные при встрече'),
            ('card_mir', '💳 Картой МИР онлайн'),
            ('card_other', '💳 Другой картой онлайн'),
        ]
        self.fields['payment_method'].label = 'Выберите способ оплаты:'
