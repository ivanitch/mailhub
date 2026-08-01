from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Mailing

TAILWIND_INPUT_CLASSES = (
    'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm '
    'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500'
)


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'class': TAILWIND_INPUT_CLASSES, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': TAILWIND_INPUT_CLASSES, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'message': forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'recipients': forms.SelectMultiple(attrs={
                'class': TAILWIND_INPUT_CLASSES + ' h-40',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Позволяет корректно отобразить уже сохранённые даты в поле datetime-local
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and start_time < timezone.now():
            # При редактировании уже идущей/прошедшей рассылки не запрещаем сохранение,
            # если start_time не менялся. Проверяем только реально новое прошлое значение.
            if not self.instance.pk or self.initial.get('start_time') != start_time:
                raise ValidationError({'start_time': 'Дата начала отправки не может быть в прошлом.'})

        if start_time and end_time and start_time >= end_time:
            raise ValidationError({'end_time': 'Дата окончания должна быть позже даты начала отправки.'})

        return cleaned_data
