from django.db import models


class Client(models.Model):
    """Получатель рассылки (клиент сервиса)."""

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Адрес электронной почты получателя, должен быть уникальным.',
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name='Ф. И. О.',
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий',
    )

    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Владелец',
        null=True,
        blank=True,
        help_text='Пользователь, которому принадлежит этот клиент.',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} <{self.email}>'
