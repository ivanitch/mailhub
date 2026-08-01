from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from users.permissions import ManagerRequiredMixin, is_manager

from .forms import MailingForm
from .models import Mailing, MailingAttempt
from .services import MailingNotAllowedError, send_mailing_now


class OwnerOrManagerVisibleMixin:
    """Для чтения: владелец видит своё, менеджер — всё."""

    def get_queryset(self):
        qs = super().get_queryset()
        if is_manager(self.request.user):
            return qs
        return qs.filter(owner=self.request.user)


class OwnerOnlyEditMixin:
    """Для изменения/удаления/отправки: только владелец, даже менеджеру нельзя."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, OwnerOrManagerVisibleMixin, ListView):
    """Список рассылок: свои, либо все — если ты менеджер."""

    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('message')
        for mailing in qs:
            mailing.update_status()
        return qs


class MailingDetailView(LoginRequiredMixin, OwnerOrManagerVisibleMixin, DetailView):
    """Просмотр одной рассылки (своя, либо любая — для менеджера).
    Статус пересчитывается при каждом открытии."""

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
        context['is_owner'] = self.object.owner_id == self.request.user.pk
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой рассылки."""

    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана.')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOnlyEditMixin, UpdateView):
    """Редактирование рассылки — только для владельца."""

    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена.')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, OwnerOnlyEditMixin, DeleteView):
    """Удаление рассылки — только для владельца."""

    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка удалена.')
        return super().form_valid(form)


class MailingSendView(LoginRequiredMixin, View):
    """Отправка рассылки по требованию через интерфейс пользователя (кнопка).
    Только владелец может отправлять свою рассылку."""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
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


class MailingToggleDisabledView(ManagerRequiredMixin, View):
    """Менеджерское действие: включить/отключить ЛЮБУЮ рассылку
    (не только свою) — п. 9 задания «Менеджеры... отключение рассылок»."""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_disabled = not mailing.is_disabled
        mailing.save(update_fields=['is_disabled'])
        if mailing.is_disabled:
            messages.success(request, 'Рассылка отключена менеджером.')
        else:
            messages.success(request, 'Рассылка снова включена.')
        return redirect('mailings:mailing_detail', pk=pk)


class MailingStatsView(LoginRequiredMixin, TemplateView):
    """Личная статистика пользователя: сколько рассылок он создал и как
    прошли попытки отправки писем по этим рассылкам."""

    template_name = 'mailings/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        my_mailings = Mailing.objects.filter(owner=user)
        for mailing in my_mailings:
            mailing.update_status()

        attempts = MailingAttempt.objects.filter(mailing__owner=user)

        context['my_mailings_count'] = my_mailings.count()
        context['my_successful_attempts'] = attempts.filter(status=MailingAttempt.Status.SUCCESS).count()
        context['my_failed_attempts'] = attempts.filter(status=MailingAttempt.Status.FAILURE).count()
        context['my_sent_total'] = attempts.count()
        return context
