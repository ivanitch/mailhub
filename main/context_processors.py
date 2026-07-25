from django.conf import settings


def app_settings(request):
    return {
        'APP_NAME': getattr(settings, 'APP_NAME', 'MyProject')
    }
