from django.urls import path
from .views import login_view, password_reset_view, custom_logout
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordResetCompleteView


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get_redirect_url(self):
        # You can specify the URL where you want to redirect after password reset
        return '/accounts/login/'  # This will redirect the user to the login page


urlpatterns = [
    path('login/', login_view, name='login'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/done/', TemplateView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),  # Custom redirect view
    path('logout/', custom_logout, name='logout'),
]