
from django.urls import path
from . import views

urlpatterns = [
    path('', views.timesheet_view, name='usertimesheet'),
    path('add-row/', views.add_timesheet_row, name='add_timesheet_row'),
    path('submit/', views.submit_timesheet_entries, name='submit_timesheet_entries'),
    path('tasks/', views.get_project_tasks, name='get_project_tasks'),
    path('subtasks/', views.get_task_subtasks, name='get_task_subtasks'),
    path('edit/<int:pk>/', views.edit_timesheet, name='edit_timesheet'),
    path('approval/update/<int:pk>/', views.load_approval_form, name='load_approval_form'),
    path('entries/', views.timesheet_entries, name='timesheet_entries'),
    path("bulk-update-approvals/", views.bulk_update_approvals, name="bulk_update_approvals"),

]
