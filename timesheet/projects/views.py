from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from core.models import Client, Project, ProjectTaskAssignment, SubTask, Task
from .forms import ClientForm, ProjectForm, ProjectTaskAssignmentForm
from django_htmx.http import trigger_client_event

def projects_view(request):
    context = {
        'clients': Client.objects.all(),
        'projects': Project.objects.select_related('client').all(),
        'assignments': ProjectTaskAssignment.objects.select_related('project', 'task', 'subtask').all(),
    }
    return render(request, 'projects/projects.html', context)

@require_POST
def save_client(request):
    instance = get_object_or_404(Client, id=request.POST.get('client_id')) if request.POST.get('client_id') else None
    form = ClientForm(request.POST, instance=instance)
    if form.is_valid():
        form.save()
        # return render(request, "projects/partials/client_table.html", {"clients": Client.objects.all()})
        return trigger_client_event(HttpResponse(), "clientSaved")
    
    # Return form with errors back to modal
    return render(request, "projects/partials/client_form.html", {"form": form})

@require_POST
def save_project(request):
    instance = get_object_or_404(Project, id=request.POST.get('project_id')) if request.POST.get('project_id') else None
    form = ProjectForm(request.POST, instance=instance)
    if form.is_valid():
        form.save()
        # return render(request, "projects/partials/project_table.html", {"projects": Project.objects.select_related('client').all()})
        return trigger_client_event(HttpResponse(), "projectSaved")
    return render(request, "projects/partials/project_form.html", {"form": form})

@require_POST
def save_assignment(request):
    instance = get_object_or_404(ProjectTaskAssignment, id=request.POST.get('assignment_id')) if request.POST.get('assignment_id') else None
    form = ProjectTaskAssignmentForm(request.POST, instance=instance)
    if form.is_valid():
        form.save()
        # return render(request, "projects/partials/assignment_table.html", {"assignments": ProjectTaskAssignment.objects.select_related('project', 'task', 'subtask').all()})
        return trigger_client_event(HttpResponse(), "assignmentSaved")
    return render(request, "projects/partials/assignment_form.html", {"form": form})

def load_assignment_form(request, assignment_id=None):
    instance = get_object_or_404(ProjectTaskAssignment, id=assignment_id) if assignment_id else None
    form = ProjectTaskAssignmentForm(instance=instance)
    return render(request, "projects/partials/assignment_form.html", {"form": form, "assignment_id": assignment_id})

def load_client_form(request, client_id=None):
    print(f"Client ID: {client_id}")  
    instance = get_object_or_404(Client, id=client_id) if client_id else None
    form = ClientForm(instance=instance)
    return render(request, "projects/partials/client_form.html", {"form": form, "client_id": client_id})

def load_project_form(request, project_id=None):
    print(f"Project ID: {project_id}")  
    instance = get_object_or_404(Project, id=project_id) if project_id else None
    form = ProjectForm(instance=instance)
    return render(request, "projects/partials/project_form.html", {"form": form, "project_id": project_id})

def get_subtasks(request):
    task_id = request.GET.get("task")
    subtasks = SubTask.objects.filter(task_id=task_id)
    return render(request, "projects/partials/subtask_dropdown.html", {"subtasks": subtasks})

def client_table(request):
    clients = Client.objects.all()
    return render(request, "projects/partials/client_table.html", {"clients": clients})


def project_table(request):
    projects = Project.objects.all()
    for project in projects:
        print('Client Name: ', project.client)
    return render(request, "projects/partials/project_table.html", {"projects": projects})

def assignment_table(request):
    assignments = ProjectTaskAssignment.objects.all()
    return render(request, "projects/partials/assignment_table.html", {"assignments": assignments})