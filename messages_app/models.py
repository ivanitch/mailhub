from django.db import models
from django.urls import reverse


class Message(models.Model):
    """Сообщение (письмо), которое можно использовать в рассылках."""

    subject = models.CharField(
        max_length=255,
        verbose_name='Тема письма',
    )
    body = models.TextField(
        verbose_name='Тело письма',
    )

    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Владелец',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def get_absolute_url(self):
        return reverse('messages_app:message_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject
