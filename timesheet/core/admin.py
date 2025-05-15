from django.contrib import admin
from .models import Resource, Project, Client, Timesheet, Department, ProjectTaskAssignment, Category, Task, SubTask, Role, Holiday, ResourceAllocation, Timesheet1

admin.site.register(Resource)
admin.site.register(Project)
admin.site.register(Client)
admin.site.register(Timesheet)
admin.site.register(Timesheet1)
admin.site.register(Department)
admin.site.register(ProjectTaskAssignment)
admin.site.register(SubTask)
admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Role)
admin.site.register(Holiday)
admin.site.register(ResourceAllocation)