from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from clients.models import Client
from messages_app.models import Message

from .forms import MailingForm
from .models import Mailing, MailingAttempt
from .services import MailingNotAllowedError, send_mailing_now


class MailingListView(ListView):
    """Список всех рассылок."""

    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('message')
        for mailing in qs:
            mailing.update_status()
        return qs


class MailingDetailView(DetailView):
    """Просмотр одной рассылки. Статус пересчитывается при каждом открытии."""

    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.select_related('recipient')[:50]
        return context


class MailingCreateView(CreateView):
    """Создание новой рассылки."""

    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана.')
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    """Редактирование рассылки."""

    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена.')
        return super().form_valid(form)


class MailingDeleteView(DeleteView):
    """Удаление рассылки."""

    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка удалена.')
        return super().form_valid(form)


class MailingSendView(View):
    """Отправка рассылки по требованию через интерфейс пользователя (кнопка)."""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        try:
            result = send_mailing_now(mailing)
        except MailingNotAllowedError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(
                request,
                f'Рассылка отправлена: успешно — {result["sent"]}, '
                f'с ошибкой — {result["failed"]} (всего получателей — {result["total"]}).',
            )
        return redirect('mailings:mailing_detail', pk=pk)
