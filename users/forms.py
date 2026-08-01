from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

TAILWIND_INPUT_CLASSES = (
    'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm '
    'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500'
)


def _apply_tailwind_classes(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault('class', TAILWIND_INPUT_CLASSES)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)
