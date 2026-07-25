from django import forms

from .models import Client

TAILWIND_INPUT_CLASSES = (
    'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm '
    'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500'
)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'client@example.com'}),
            'full_name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Иванов Иван Иванович'}),
            'comment': forms.Textarea(attrs={'class': TAILWIND_INPUT_CLASSES, 'rows': 4}),
        }
