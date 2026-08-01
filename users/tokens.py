from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    """Токен для подтверждения email при регистрации.

    В отличие от стандартного PasswordResetTokenGenerator, в хэш добавлен
    флаг is_active — благодаря этому ссылка подтверждения автоматически
    становится недействительной после того, как пользователь один раз
    ей воспользовался (is_active меняется с False на True).
    """

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.is_active}'


email_confirmation_token = EmailConfirmationTokenGenerator()
