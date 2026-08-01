from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ClientForm
from .models import Client


class ClientListView(ListView):
    """Список всех получателей рассылки."""

    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20


class ClientDetailView(DetailView):
    """Просмотр одного получателя рассылки."""

    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'


class ClientCreateView(SuccessMessageMixin, CreateView):
    """Добавление нового получателя рассылки."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    # %(full_name)s подставит атрибут full_name созданного объекта
    success_message = 'Получатель "%(full_name)s" успешно добавлен.'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(SuccessMessageMixin, UpdateView):
    """Редактирование получателя рассылки."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    # Автоматически подставляет full_name из обновленной модели
    success_message = 'Данные получателя "%(full_name)s" обновлены.'


class ClientDeleteView(DeleteView):
    """Удаление получателя рассылки."""

    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        # Передаем имя перед удалением, пока объект self.object еще доступен
        messages.success(self.request, f'Получатель "{self.object.full_name}" был успешно удалён.')
        return super().form_valid(form)
