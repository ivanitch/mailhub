"""Логика отправки рассылок, переиспользуемая между веб-интерфейсом
и management-командой (см. mailings/management/commands/send_mailing.py)."""

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt
from main.views import invalidate_home_stats_cache

invalidate_home_stats_cache()


class MailingNotAllowedError(Exception):
    """Отправка запрещена (сейчас не входит в разрешённое окно времени, либо отключена)."""


def send_mailing_now(mailing: Mailing) -> dict:
    """Выполняет отправку рассылки прямо сейчас.

    1. Проверяет, что текущее время находится между start_time и end_time
       и что рассылка не отключена менеджером.
    2. Для каждого получателя отправляет письмо через send_mail().
    3. Каждая попытка (успех/ошибка) сохраняется как MailingAttempt.
       Записи создаются одним batch-запросом через bulk_create().

    Возвращает словарь с итогами: {'sent': int, 'failed': int, 'total': int}.
    Бросает MailingNotAllowedError, если отправка сейчас не разрешена.
    """
    mailing.update_status()

    if not mailing.is_sending_allowed():
        raise MailingNotAllowedError(
            'Отправка запрещена: текущее время вне периода '
            f'{timezone.localtime(mailing.start_time):%d.%m.%Y %H:%M} — '
            f'{timezone.localtime(mailing.end_time):%d.%m.%Y %H:%M}, '
            'либо рассылка отключена менеджером.'
        )

    recipients = list(mailing.recipients.all())
    attempts_to_create = []
    sent_count = 0
    failed_count = 0

    for client in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )
        except Exception as exc:  # noqa: BLE001 — фиксируем любую ошибку отправки как попытку
            failed_count += 1
            attempts_to_create.append(
                MailingAttempt(
                    mailing=mailing,
                    recipient=client,
                    status=MailingAttempt.Status.FAILURE,
                    server_response=str(exc),
                )
            )
        else:
            sent_count += 1
            attempts_to_create.append(
                MailingAttempt(
                    mailing=mailing,
                    recipient=client,
                    status=MailingAttempt.Status.SUCCESS,
                    server_response='OK',
                )
            )

    # Создание попыток одним batch-запросом, как того требует задание.
    MailingAttempt.objects.bulk_create(attempts_to_create)

    return {'sent': sent_count, 'failed': failed_count, 'total': len(recipients)}
