from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from users.permissions import is_manager

from .forms import ClientForm
from .models import Client


class OwnerOrManagerVisibleMixin:
    """Для чтения (список/детали): владелец видит своё, менеджер — всё,
    остальные авторизованные — только своё."""

    def get_queryset(self):
        qs = super().get_queryset()
        if is_manager(self.request.user):
            return qs
        return qs.filter(owner=self.request.user)


class OwnerOnlyEditMixin:
    """Для изменения/удаления: доступно ТОЛЬКО владельцу — даже менеджер
    не может редактировать или удалять чужие данные (см. задание, п. 9)."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class ClientListView(LoginRequiredMixin, OwnerOrManagerVisibleMixin, ListView):
    """Список получателей рассылки: свои, либо все — если ты менеджер."""

    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20


class ClientDetailView(LoginRequiredMixin, OwnerOrManagerVisibleMixin, DetailView):
    """Просмотр одного получателя рассылки (свой, либо любой — для менеджера)."""

    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'


class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Добавление нового получателя рассылки."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    # %(full_name)s подставит атрибут full_name созданного объекта
    success_message = 'Получатель "%(full_name)s" успешно добавлен.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, OwnerOnlyEditMixin, SuccessMessageMixin, UpdateView):
    """Редактирование получателя рассылки — только для владельца."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    success_message = 'Данные получателя "%(full_name)s" обновлены.'


class ClientDeleteView(LoginRequiredMixin, OwnerOnlyEditMixin, DeleteView):
    """Удаление получателя рассылки — только для владельца."""

    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        messages.success(self.request, f'Получатель "{self.object.full_name}" был успешно удалён.')
        return super().form_valid(form)
