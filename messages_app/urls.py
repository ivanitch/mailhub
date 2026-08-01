from django.urls import path

from . import views

app_name = 'messages_app'

urlpatterns = [
    path('', views.MessageListView.as_view(), name='message_list'),
    path('add/', views.MessageCreateView.as_view(), name='message_create'),
    path('<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('<int:pk>/edit/', views.MessageUpdateView.as_view(), name='message_update'),
    path('<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
]
