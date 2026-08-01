from django.contrib import messages
from django.core.cache import cache
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import MessageForm
from .models import Message

MESSAGE_LIST_CACHE_KEY = 'messages:list'
MESSAGE_LIST_CACHE_TIMEOUT = 60  # секунд


def invalidate_message_list_cache():
    cache.delete(MESSAGE_LIST_CACHE_KEY)


@method_decorator(cache_control(private=True, max_age=15), name='dispatch')
class MessageListView(ListView):
    """Список всех сообщений (писем)."""

    model = Message
    template_name = 'messages_app/message_list.html'
    context_object_name = 'messages_list'
    paginate_by = 20

    def get_queryset(self):
        cached = cache.get(MESSAGE_LIST_CACHE_KEY)
        if cached is not None:
            return cached
        qs = list(Message.objects.all())
        cache.set(MESSAGE_LIST_CACHE_KEY, qs, MESSAGE_LIST_CACHE_TIMEOUT)
        return qs


class MessageDetailView(DetailView):
    """Просмотр одного сообщения."""

    model = Message
    template_name = 'messages_app/message_detail.html'
    context_object_name = 'message_obj'


class MessageCreateView(CreateView):
    """Добавление нового сообщения."""

    model = Message
    form_class = MessageForm
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:message_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано.')
        response = super().form_valid(form)
        invalidate_message_list_cache()
        from main.views import invalidate_home_stats_cache
        invalidate_home_stats_cache()
        return response


class MessageUpdateView(UpdateView):
    """Редактирование сообщения."""

    model = Message
    form_class = MessageForm
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено.')
        response = super().form_valid(form)
        invalidate_message_list_cache()
        return response


class MessageDeleteView(DeleteView):
    """Удаление сообщения."""

    model = Message
    template_name = 'messages_app/message_confirm_delete.html'
    success_url = reverse_lazy('messages_app:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение удалено.')
        response = super().form_valid(form)
        invalidate_message_list_cache()
        from main.views import invalidate_home_stats_cache
        invalidate_home_stats_cache()
        return response
