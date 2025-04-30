"""
URL configuration for timesheet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view 
from dashboard.views import dashboard_view
from resources.views import resources_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', login_view, name='login'),
    path('logout/', login_view, name='logout'),
    path('', login_view, name='login'),
    
    path('accounts/', include('accounts.urls')),
    
    path('dashboard/', include('dashboard.urls')),
    path('usertimesheet/', include('usertimesheet.urls')),
    path('reports/', include('reports.urls')),
    path('projects/', include('projects.urls')),
    path('resources/', include('resources.urls')),
    path('taskmanager/', include('taskmanager.urls')),
    
]