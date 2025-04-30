from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.projects_view, name="projects"),
    path("save-client/", views.save_client, name="save_client"),
    path("save-project/", views.save_project, name="save_project"),
    path("save-assignment/", views.save_assignment, name="save_assignment"),

    path("load-client-form/<int:client_id>/", views.load_client_form, name="edit_client"),
    path("load-client-form/", views.load_client_form, name="add_client_form"),
    
    path("load-project-form/<int:project_id>/", views.load_project_form, name="edit_project"),
    path("load-project-form/", views.load_project_form, name="add_project_form"),
    
    path("load-assignment-form/<int:assignment_id>/", views.load_assignment_form, name="edit_assignment"),
    path("load-assignment-form/", views.load_assignment_form, name="add_assignment_form"),

    path("projects/get-subtasks/", views.get_subtasks, name="get_subtasks"),

    path('clients/table/', views.client_table, name='client_table'),
    path('projects/table/', views.project_table, name='project_table'),
    path('assignments/table/', views.assignment_table, name='assignment_table'),
]