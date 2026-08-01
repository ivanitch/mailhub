from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from clients.models import Client
from messages_app.models import Message
from mailings.models import Mailing, MailingAttempt


class HomeView(TemplateView):
    """Главная страница: сводная статистика по рассылкам, клиентам и попыткам отправки."""

    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статус хранится в БД, но может быть устаревшим — пересчитываем перед подсчётом.
        for mailing in Mailing.objects.all():
            mailing.update_status()

        now = timezone.now()
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(
            status=Mailing.Status.STARTED,
            start_time__lte=now,
            end_time__gte=now,
        ).count()
        context['unique_recipients'] = Client.objects.count()
        context['total_messages'] = Message.objects.count()
        context['successful_attempts'] = MailingAttempt.objects.filter(
            status=MailingAttempt.Status.SUCCESS,
        ).count()
        context['failed_attempts'] = MailingAttempt.objects.filter(
            status=MailingAttempt.Status.FAILURE,
        ).count()
        return context
