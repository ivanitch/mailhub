from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import MessageForm
from .models import Message


class MessageListView(ListView):
    """Список всех сообщений (писем)."""

    model = Message
    template_name = 'messages_app/message_list.html'
    context_object_name = 'messages_list'
    paginate_by = 20


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
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    """Редактирование сообщения."""

    model = Message
    form_class = MessageForm
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено.')
        return super().form_valid(form)


class MessageDeleteView(DeleteView):
    """Удаление сообщения."""

    model = Message
    template_name = 'messages_app/message_confirm_delete.html'
    success_url = reverse_lazy('messages_app:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение удалено.')
        return super().form_valid(form)
