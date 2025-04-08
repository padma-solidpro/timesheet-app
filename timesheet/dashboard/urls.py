from django.urls import path
from . import views
from .views import dashboard_view

# urlpatterns = [path('', dashboard_view, name='dashboard')]
urlpatterns = [path ('', views.dashboard_view, name='dashboard'),]