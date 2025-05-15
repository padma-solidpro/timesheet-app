from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Project, Resource, ProjectTaskAssignment, ResourceAllocation
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import date, timedelta
from django.http import JsonResponse  # Still useful for modal content

@login_required
def resource_allocation_view(request):
    user = request.user
    resource = Resource.objects.get(user=user)
    projects = Project.objects.filter(project_lead=resource)
    return render(request, 'resource_allocation/resource_allocation.html', {'projects': projects})

def get_project_tasks_subtasks(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    task_assignments = ProjectTaskAssignment.objects.filter(project=project).order_by('task__name', 'subtask__name')
    context = {'project': project, 'task_assignments': task_assignments}
    return render(request, 'resource_allocation/allocation_table.html', context)

def get_assign_resource_modal(request, project_id, task_id, subtask_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id)
    subtask = get_object_or_404(SubTask, id=subtask_id)
    resources = Resource.objects.all()  # You might want to filter this based on roles, etc.
    context = {'project_id': project_id, 'task_id': task_id, 'subtask_id': subtask_id, 'resources': resources}
    return render(request, 'resource_allocation/assign_resource_modal_content.html', context)

def assign_resource(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        task_id = request.POST.get('task_id')
        subtask_id = request.POST.get('subtask_id')
        resource_id = request.POST.get('resource_id')
        assigned_hours = request.POST.get('assigned_hours')

        project = get_object_or_404(Project, id=project_id)
        task = get_object_or_404(Task, id=task_id)
        subtask = get_object_or_404(SubTask, id=subtask_id)
        resource = get_object_or_404(Resource, id=resource_id)

        assigning_user = request.user
        assigned_by_resource = Resource.objects.get(user=assigning_user)

        ResourceAllocation.objects.create(
            project=project,
            task=task,
            subtask=subtask,
            resource=resource,
            assigned_hours=assigned_hours,
            week_start_date=date.today() - timedelta(days=date.today().weekday()),
            assigned_by=assigned_by_resource
        )

        # Render the updated subtask row
        task_assignment = get_object_or_404(ProjectTaskAssignment, project=project, task=task, subtask=subtask)
        allocations = ResourceAllocation.objects.filter(project=project, task=task, subtask=subtask)
        context = {'subtask_assignment': task_assignment, 'allocations': allocations, 'project': project}
        return render(request, 'resource_allocation/subtask_allocations.html', context)
    return HttpResponse("Error assigning resource.", status=400)

def remove_resource_allocation(request):
    if request.method == 'POST':
        allocation_id = request.POST.get('allocation_id')
        try:
            allocation = ResourceAllocation.objects.get(id=allocation_id)
            project = allocation.project
            task = allocation.task
            subtask = allocation.subtask
            allocation.delete()

            # Render the updated subtask row
            task_assignment = get_object_or_404(ProjectTaskAssignment, project=project, task=task, subtask=subtask)
            allocations = ResourceAllocation.objects.filter(project=project, task=task, subtask=subtask)
            context = {'subtask_assignment': task_assignment, 'allocations': allocations, 'project': project}
            return render(request, 'resource_allocation/subtask_allocations.html', context)
        except ResourceAllocation.DoesNotExist:
            return HttpResponse("Allocation not found.", status=404)
    return HttpResponse("Error removing allocation.", status=400)