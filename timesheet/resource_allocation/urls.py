from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_allocation_page, name='resource_allocation'),
    path('load-assign-resource-form/<int:project_id>/<int:task_id>/<int:subtask_id>/', views.load_assign_resource_form, name='load_assign_resource_form'),
    path('assign-resource/', views.assign_resource, name='assign_resource'),
    path('delete-assignment/<int:allocation_id>/', views.delete_assignment, name='delete_assignment'),
]
