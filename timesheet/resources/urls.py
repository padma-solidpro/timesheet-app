from django.urls import path
from . import views

urlpatterns = [
    path('', views.resources_view, name='resources'),
    path('save/', views.save_resource, name='save_resource'),
    path('new/', views.load_new_resource_form, name='load_new_resource_form'),
    path('edit/<int:pk>/', views.load_resource_form, name='load_resource_form'),
    path('reporting_options/', views.load_reporting_to_options, name='load_reporting_to_options'),
]