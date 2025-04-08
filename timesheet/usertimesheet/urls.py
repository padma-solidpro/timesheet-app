from django.urls import path
from .views import usertimesheet_view
urlpatterns = [
    path('', usertimesheet_view, name='usertimesheet'),
]