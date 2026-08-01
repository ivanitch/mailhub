from django.core.cache import cache
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from clients.models import Client
from mailings.models import Mailing, MailingAttempt
from messages_app.models import Message

# Ключ и время жизни кеша сводной статистики на главной странице.
HOME_STATS_CACHE_KEY = 'main:home_stats'
HOME_STATS_CACHE_TIMEOUT = 60  # секунд


def invalidate_home_stats_cache():
    """Сбросить кеш статистики главной страницы (вызывается при изменении
    данных, которые на неё влияют)."""
    cache.delete(HOME_STATS_CACHE_KEY)


@method_decorator(cache_control(private=True, max_age=30), name='dispatch')
class HomeView(TemplateView):
    """Главная страница: сводная статистика по рассылкам, клиентам и попыткам отправки."""

    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self._get_stats())
        return context

    def _get_stats(self):
        cached = cache.get(HOME_STATS_CACHE_KEY)
        if cached is not None:
            return cached

        # Статус хранится в БД, но может быть устаревшим — пересчитываем перед подсчётом.
        for mailing in Mailing.objects.all():
            mailing.update_status()

        now = timezone.now()
        stats = {
            'total_mailings': Mailing.objects.count(),
            'active_mailings': Mailing.objects.filter(
                status=Mailing.Status.STARTED,
                start_time__lte=now,
                end_time__gte=now,
            ).count(),
            'unique_recipients': Client.objects.count(),
            'total_messages': Message.objects.count(),
            'successful_attempts': MailingAttempt.objects.filter(
                status=MailingAttempt.Status.SUCCESS,
            ).count(),
            'failed_attempts': MailingAttempt.objects.filter(
                status=MailingAttempt.Status.FAILURE,
            ).count(),
        }
        cache.set(HOME_STATS_CACHE_KEY, stats, HOME_STATS_CACHE_TIMEOUT)
        return stats
