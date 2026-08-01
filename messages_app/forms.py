from django import forms

from .models import Message

TAILWIND_INPUT_CLASSES = (
    'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm '
    'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500'
)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Тема письма'}),
            'body': forms.Textarea(attrs={'class': TAILWIND_INPUT_CLASSES, 'rows': 8, 'placeholder': 'Текст письма...'}),
        }
