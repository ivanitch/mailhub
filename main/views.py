from django.views.generic import TemplateView

from clients.models import Client


class HomeView(TemplateView):
    """Главная страница: сводная статистика по рассылкам, клиентам и попыткам отправки."""

    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['unique_recipients'] = Client.objects.count()

        return context
