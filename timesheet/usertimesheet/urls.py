from django.urls import path
from . import views

urlpatterns = [
    path('', views.usertimesheet_view, name='usertimesheet'),
    path('get-project-row/', views.get_project_row, name='get_project_row'),
    path('edit/<int:entry_id>/', views.edit_timesheet, name='edit_timesheet'),
]
