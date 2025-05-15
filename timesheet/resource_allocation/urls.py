from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_allocation_view, name='resource_allocation'),
    path('get-project-tasks/<int:project_id>/', views.get_project_tasks_subtasks, name='get_project_tasks_subtasks'),
    path('get-assign-resource-modal/<int:project_id>/<int:task_id>/<int:subtask_id>/', views.get_assign_resource_modal, name='get_assign_resource_modal'),
    path('assign-resource/', views.assign_resource, name='assign_resource'),
    path('remove-resource-allocation/', views.remove_resource_allocation, name='remove_resource_allocation'),
]