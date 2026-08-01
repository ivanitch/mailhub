from django.urls import path

from . import views

app_name = 'mailings'

urlpatterns = [
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/add/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/toggle-disabled/', views.MailingToggleDisabledView.as_view(), name='mailing_toggle_disabled'),
    path('mailings/stats/', views.MailingStatsView.as_view(), name='stats'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.MailingSendView.as_view(), name='mailing_send'),
]
