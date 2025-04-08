from django.contrib import admin
from .models import Resource, Project, Client, Timesheet

admin.site.register(Resource)
admin.site.register(Project)
admin.site.register(Client)
admin.site.register(Timesheet)
