from django.shortcuts import render, get_object_or_404, redirect
from core.models import Project, Task, SubTask, ResourceAllocation, Resource, ProjectTaskAssignment, Role
from django.db.models import Sum
from django.http import JsonResponse
from django.db import connection
from datetime import datetime

def resource_allocation_page(request):
    user = request.user
    resource = Resource.objects.get(user=user)
    projects = Project.objects.filter(project_lead=resource)

    project_id = request.GET.get('project')
    selected_project = Project.objects.filter(id=project_id).first() if project_id else None

    pta_qs = ProjectTaskAssignment.objects.filter(project=selected_project) if selected_project else ProjectTaskAssignment.objects.none()

    tasks = Task.objects.filter(id__in=pta_qs.values_list('task_id', flat=True).distinct())
    subtasks = SubTask.objects.filter(id__in=pta_qs.values_list('subtask_id', flat=True).exclude(subtask_id__isnull=True).distinct())

    allocations = ResourceAllocation.objects.filter(project=selected_project).select_related('resource', 'task', 'subtask')

    # Fetch availability from materialized view
    with connection.cursor() as cursor:
        cursor.execute("SELECT resource_id, available_hours FROM resource_availability1_mv")
        availability_map = {row[0]: row[1] for row in cursor.fetchall()}

    context = {
        'projects': projects,
        'selected_project_id': project_id,
        'tasks': tasks,
        'subtasks': subtasks,
        'allocations': allocations,
        'availability_map': availability_map,
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'resource_allocation/partials/tree_table.html', context)

    return render(request, 'resource_allocation/resource_allocation_page.html', context)

def load_assign_resource_form(request, project_id, task_id, subtask_id):
    # resources = Resource.objects.all()
    resources = Resource.objects.select_related('role').exclude(role__isnull=True)

    # roles = Resource.objects.values_list('role__name', flat=True).distinct()
    roles = Role.objects.filter(id__in=Resource.objects.exclude(role=None).values_list('role_id', flat=True)).distinct()

    with connection.cursor() as cursor:
        cursor.execute("SELECT resource_id, available_hours FROM resource_availability1_mv")
        availability_map = {row[0]: row[1] for row in cursor.fetchall()}

    week_start_date = request.GET.get('week_start_date') or datetime.today().date()

    return render(request, 'resource_allocation/partials/assign_resource_modal_form.html', {
        'project_id': project_id,
        'task_id': task_id,
        'subtask_id': subtask_id,
        'resources': resources,
        'availability_map': availability_map,
        'roles': roles, 
        'week_start_date': week_start_date,
    })

def assign_resource(request):
    if request.method == 'POST':
        resource_ids = request.POST.getlist('resource_ids')
        hours_list = request.POST.getlist('assigned_hours')
        project_id = request.POST.get('project_id')
        task_id = request.POST.get('task_id')
        subtask_id = request.POST.get('subtask_id')
        week_start_str  = request.POST.get('week_start_date')
        week_start_date = datetime.strptime(week_start_str, '%B %d, %Y').date()


        assigned_by = Resource.objects.filter(user=request.user).first()

        for res_id, hrs in zip(resource_ids, hours_list):
            ResourceAllocation.objects.create(
                resource_id=res_id,
                project_id=project_id,
                task_id=task_id,
                subtask_id=subtask_id,
                week_start_date=week_start_date,
                assigned_hours=hrs,
                assigned_by=assigned_by,
            )
        # return redirect('resource_allocation')
        allocations = ResourceAllocation.objects.filter(project_id=project_id)
        html = render_to_string('resource_allocation/partials/allocation_table.html', {
            'allocations': allocations
        }, request=request)

        return HttpResponse(html)

def delete_assignment(request, allocation_id):
    allocation = get_object_or_404(ResourceAllocation, id=allocation_id)
    allocation.delete()
    return JsonResponse({'success': True})
