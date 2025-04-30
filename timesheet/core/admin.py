from django.contrib import admin
from .models import Resource, Project, Client, Timesheet, Department, ProjectTaskAssignment, Category, Task, SubTask, Role

admin.site.register(Resource)
admin.site.register(Project)
admin.site.register(Client)
admin.site.register(Timesheet)
admin.site.register(Department)
admin.site.register(ProjectTaskAssignment)
admin.site.register(SubTask)
admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Role)