from django.views.generic import TemplateView

from clients.models import Client
from messages_app.models import Message


class HomeView(TemplateView):
    """Главная страница: сводная статистика по рассылкам, клиентам и попыткам отправки."""

    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['clients'] = Client.objects.count()
        context['total_messages'] = Message.objects.count()

        return context
