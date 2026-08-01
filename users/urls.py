from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import LoginForm, StyledPasswordResetForm, StyledSetPasswordForm

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/pending/', views.RegistrationPendingView.as_view(), name='registration_pending'),
    path('confirm-email/<uidb64>/<token>/', views.ConfirmEmailView.as_view(), name='confirm_email'),

    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=LoginForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.txt',
        subject_template_name='registration/password_reset_subject.txt',
        form_class=StyledPasswordResetForm,
        success_url=reverse_lazy('users:password_reset_done'),
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        form_class=StyledSetPasswordForm,
        success_url=reverse_lazy('users:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
]
