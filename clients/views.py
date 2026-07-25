from django.contrib import messages
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


class ClientCreateView(CreateView):
    """Добавление нового получателя рассылки."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
        messages.success(self.request, 'Получатель рассылки успешно добавлен.')
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    """Редактирование получателя рассылки."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные получателя обновлены.')
        return super().form_valid(form)


class ClientDeleteView(DeleteView):
    """Удаление получателя рассылки."""

    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель рассылки удалён.')
        return super().form_valid(form)
