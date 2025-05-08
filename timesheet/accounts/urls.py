from django.urls import path
from .views import login_view, custom_logout
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', custom_logout, name='logout'),

    # Password reset views using built-in Django auth
     path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            success_url='/accounts/password_reset/done/',
            from_email='spdt-apps-svc@solidpro-es.com',  # ✅ explicitly set
        ),
        name='password_reset'
    ),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),

    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
    ), name='password_reset_confirm'),

    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]


# from django.urls import path
# from .views import login_view, password_reset_view, custom_logout
# from django.contrib.auth.views import PasswordResetConfirmView
# from django.contrib.auth.views import LogoutView
# from django.views.generic import TemplateView
# from django.contrib.auth.views import PasswordResetCompleteView
# from django.contrib import messages
# from django.shortcuts import redirect
# from django.contrib.auth import views as auth_views


# # class CustomPasswordResetCompleteView(PasswordResetCompleteView):
# #     def get_redirect_url(self):
# #         # You can specify the URL where you want to redirect after password reset
# #         return '/accounts/login/'  # This will redirect the user to the login page

# class CustomPasswordResetCompleteView(PasswordResetCompleteView):
#     def get(self, request, *args, **kwargs):
#         messages.success(request, 'Your password has been reset. You can now log in.')
#         return redirect('login')  # or use reverse() for dynamic URL resolution

# urlpatterns = [
#     path('login/', login_view, name='login'),
#     path('password_reset/', password_reset_view, name='password_reset'),
#     path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
#     path('password_reset/done/', TemplateView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
#     # path('password_reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),  # Custom redirect view
#     path('accounts/password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
#     path('logout/', custom_logout, name='logout'),
# ]