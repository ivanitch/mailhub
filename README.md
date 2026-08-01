# MailHub — сервис управления рассылками

Веб-приложение на Django для управления рассылками сообщений клиентам:
клиенты, письма, рассылки с расписанием, статистика, роли, кеширование.

## Возможности

- **Клиенты / Сообщения / Рассылки** — полный CRUD.
- **Рассылки** — статус вычисляется динамически (Создана / Запущена /
  Завершена), отправка по кнопке или `python manage.py send_mailing <id>`,
  журнал попыток (успех/ошибка).
- **Пользователи** — регистрация с подтверждением email, вход/выход,
  восстановление пароля.
- **Роли** — Пользователь (видит и правит только своё), Менеджер (видит
  всё, блокирует пользователей, отключает любые рассылки).
- **Статистика** — общая на главной, персональная у каждого пользователя.
- **Кеширование** — серверное (данные) + клиентское (`Cache-Control`).

## Стек

Python 3.12 · Django 6.0 · Tailwind CSS (`django-tailwind`) · PostgreSQL · Redis · Yandex SMTP

## Быстрый старт

```bash
cp .env.example .env

cd theme/static_src && npm install && cd ../..
uv run python manage.py tailwind build

uv run python manage.py migrate        # создаст в т.ч. группу Managers
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Открыть: http://127.0.0.1:8000/ · Админка: http://127.0.0.1:8000/admin/

Роль менеджера выдаётся через `/admin/` → пользователь → группа `Managers`.

## Полезные команды

```bash
uv run python manage.py send_mailing <id>   # отправить рассылку из консоли
uv run python manage.py tailwind start      # пересборка CSS на лету при разработке
```
