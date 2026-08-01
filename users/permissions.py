from django.contrib.auth.mixins import UserPassesTestMixin


def is_manager(user):
    """Менеджер — суперпользователь либо участник группы 'Managers'.

    Обычные is_staff здесь ни при чём: is_staff даёт доступ в /admin/,
    а роль «Менеджер» — это бизнес-роль внутри самого приложения
    (просмотр всех клиентов/рассылок, блокировка пользователей,
    отключение чужих рассылок).
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    return user.is_superuser or user.groups.filter(name='Managers').exists()


class ManagerRequiredMixin(UserPassesTestMixin):
    """Пускает только менеджеров (см. is_manager).

    Поведение по умолчанию от UserPassesTestMixin/AccessMixin нам подходит:
    - анонимного пользователя редиректит на страницу входа;
    - авторизованного, но не менеджера — 403 Forbidden.
    """

    def test_func(self):
        return is_manager(self.request.user)
