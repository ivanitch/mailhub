from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Mailing(models.Model):
    """Рассылка: письмо (Message), отправляемое списку клиентов (Client)
    в промежутке времени [start_time, end_time]."""

    class Status(models.TextChoices):
        CREATED = 'created', 'Создана'
        STARTED = 'started', 'Запущена'
        FINISHED = 'finished', 'Завершена'

    start_time = models.DateTimeField(
        verbose_name='Дата и время начала отправки',
        help_text='С какого момента рассылка может быть запущена.',
    )
    end_time = models.DateTimeField(
        verbose_name='Дата и время окончания отправки',
        help_text='До какого момента разрешено выполнять отправку.',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        verbose_name='Статус',
    )

    message = models.ForeignKey(
        'messages_app.Message',
        on_delete=models.PROTECT,
        related_name='mailings',
        verbose_name='Сообщение',
    )
    recipients = models.ManyToManyField(
        'clients.Client',
        related_name='mailings',
        verbose_name='Получатели',
        blank=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец',
        null=True,
        blank=True,
    )
    is_disabled = models.BooleanField(
        default=False,
        verbose_name='Отключена менеджером',
        help_text='Если включено — рассылку нельзя запустить, даже в разрешённом окне времени.',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-start_time']

    def __str__(self):
        return f'Рассылка «{self.message.subject}» ({self.get_status_display()})'

    def compute_status(self):
        """Вычисляет статус рассылки на основе текущего времени, не сохраняя его."""
        now = timezone.now()
        if now < self.start_time:
            return self.Status.CREATED
        if self.start_time <= now <= self.end_time:
            return self.Status.STARTED
        return self.Status.FINISHED

    def update_status(self):
        """Пересчитывает статус и сохраняет его в БД, если он изменился."""
        new_status = self.compute_status()
        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status'])
        return self.status

    def is_sending_allowed(self):
        """Разрешена ли отправка прямо сейчас (окно времени и отсутствие блокировки)."""
        now = timezone.now()
        return (not self.is_disabled) and (self.start_time <= now <= self.end_time)

    def clean(self):
        errors = {}
        now = timezone.now()

        if self.start_time and self.start_time < now:
            errors['start_time'] = 'Дата начала отправки не может быть в прошлом.'

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            errors['end_time'] = 'Дата окончания должна быть позже даты начала отправки.'

        if errors:
            raise ValidationError(errors)


class MailingAttempt(models.Model):
    """Попытка отправки письма в рамках рассылки."""

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Успешно'
        FAILURE = 'failure', 'Не успешно'

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время попытки',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        verbose_name='Статус',
    )
    server_response = models.TextField(
        blank=True,
        verbose_name='Ответ почтового сервера',
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка',
    )

    # Дополнительное (необязательное) поле сверх задания — помогает понять,
    # какому именно получателю относится попытка, для диагностики и статистики.
    recipient = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        related_name='mailing_attempts',
        verbose_name='Получатель',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['-attempt_time']

    def __str__(self):
        return f'{self.get_status_display()} — {self.mailing} ({self.attempt_time:%Y-%m-%d %H:%M})'
