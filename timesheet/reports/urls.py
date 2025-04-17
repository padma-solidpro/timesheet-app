from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_view, name='reports'),  # Main page
    path('data/', views.reports_partial_view, name='report_data'),  # HTMX partial content
]
