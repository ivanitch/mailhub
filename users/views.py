from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import RegisterForm
from .tokens import email_confirmation_token


class RegisterView(CreateView):
    """Регистрация нового пользователя. Аккаунт создаётся неактивным,
    пока пользователь не перейдёт по ссылке подтверждения из письма."""

    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:registration_pending')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        self._send_confirmation_email(user)
        return super().form_valid(form)

    def _send_confirmation_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_confirmation_token.make_token(user)
        confirm_url = self.request.build_absolute_uri(
            reverse('users:confirm_email', kwargs={'uidb64': uid, 'token': token})
        )
        message = render_to_string('registration/email_confirmation_email.txt', {
            'user': user,
            'confirm_url': confirm_url,
            'app_name': getattr(settings, 'APP_NAME', 'MailHub'),
        })
        send_mail(
            subject=f'Подтвердите email — {getattr(settings, "APP_NAME", "MailHub")}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class RegistrationPendingView(TemplateView):
    """Промежуточная страница: «мы отправили письмо, проверьте почту»."""

    template_name = 'registration/registration_pending.html'


class ConfirmEmailView(View):
    """Обрабатывает переход по ссылке из письма подтверждения."""

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and email_confirmation_token.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Email подтверждён, добро пожаловать!')
            return redirect('main:home')

        messages.error(request, 'Ссылка подтверждения недействительна или уже была использована.')
        return redirect('users:login')
