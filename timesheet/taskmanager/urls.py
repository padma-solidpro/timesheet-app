# taskmanager/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_page, name='taskmanager'),

    # Category
    path('add/category/', views.add_category, name='add_category'),
    path('edit/category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete/category/<int:pk>/', views.delete_category, name='delete_category'),

    # Task
    path('add/task/', views.add_task, name='add_task'),
    path('edit/task/<int:pk>/', views.edit_task, name='edit_task'),
    path('delete/task/<int:pk>/', views.delete_task, name='delete_task'),

    # SubTask
    path('add/subtask/', views.add_subtask, name='add_subtask'),
    path('edit/subtask/<int:pk>/', views.edit_subtask, name='edit_subtask'),
    path('delete/subtask/<int:pk>/', views.delete_subtask, name='delete_subtask'),

    # HTMX dynamic cascading form
    path('load-tasks/', views.load_tasks_for_category, name='load_tasks_for_category'),
    path('save-full-task/', views.save_full_task, name='save_full_task'),
    path('add/full-task/', views.cascading_task_form, name='cascading_task_form'),
] 
