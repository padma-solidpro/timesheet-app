from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from datetime import date
from core.models import Timesheet, Resource, Project
from .forms import TimesheetForm



@login_required
def usertimesheet_view(request):
    user = request.user
    manager = get_object_or_404(Resource, user=user)
    employee_list = Resource.objects.filter(reporting_to=manager)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if not employee_id:
            return HttpResponse("Please select an employee.", status=400)

        resource = Resource.objects.get(id=employee_id)
        today = date.today()

        if Timesheet.objects.filter(resource=resource, date=today).exists():
            messages.error(request, "Timesheet already exists for today!")
            return HttpResponse("Timesheet already exists for today!", status=400)

        entries = []
        i = 0
        while True:
            pid = request.POST.get(f'project_{i}')
            task = request.POST.get(f'task_{i}')
            hrs = request.POST.get(f'hours_{i}')
            if not (pid and task and hrs):
                break
            entries.append(Timesheet(resource=resource, project_id=pid, task_description=task, hours=hrs))
            i += 1

        Timesheet.objects.bulk_create(entries)
        recent_entries = Timesheet.objects.select_related('resource', 'project__client', 'resource__department').order_by('-id')[:10]
        html = render_to_string('usertimesheet/recent_entries.html', {'recent_entries': recent_entries})
        return HttpResponse(html)

    recent_entries = Timesheet.objects.select_related('resource', 'project__client', 'resource__department').order_by('-id')[:10]
    return render(request, 'usertimesheet/user_timesheet.html', {
        'form': TimesheetForm(),
        'employee_list': employee_list,
        'recent_entries': recent_entries
    })


@login_required
def get_project_row(request):
    employee_id = request.GET.get('employee_id')
    index = request.GET.get('index', '0')

    if employee_id:
        resource = get_object_or_404(Resource, id=employee_id)
        projects = resource.assigned_projects.all()
    else:
        projects = Project.objects.none()

    index = int(request.GET.get('index', 0))
    html = render_to_string('usertimesheet/project_row.html', {
        'project_list': projects,
        'index': index,
    })
    return HttpResponse(html)


@login_required
def edit_timesheet(request, entry_id):
    entry = get_object_or_404(Timesheet, id=entry_id)

    if request.method == 'POST':
        entry.task_description = request.POST.get('task_description')
        entry.hours = request.POST.get('hours')
        entry.save()
        recent_entries = Timesheet.objects.select_related('resource', 'project__client', 'resource__department').order_by('-id')[:10]
        html = render_to_string('usertimesheet/recent_entries.html', {'recent_entries': recent_entries})
        return HttpResponse(html)

    html = render_to_string('usertimesheet/edit_modal.html', {'entry': entry})
    return HttpResponse(html)
