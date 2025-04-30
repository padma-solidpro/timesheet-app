# taskmanager/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_page, name='taskmanager'),  # 👈 Give it this name
    path('add-category/', views.add_category, name='add_category'),
    path('add-task/', views.add_task, name='add_task'),
    path('add-subtask/', views.add_subtask, name='add_subtask'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('edit-task/<int:pk>/', views.edit_task, name='edit_task'),
    path('edit-subtask/<int:pk>/', views.edit_subtask, name='edit_subtask'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('delete-task/<int:pk>/', views.delete_task, name='delete_task'),
    path('delete-subtask/<int:pk>/', views.delete_subtask, name='delete_subtask'),
]
