from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Client, Project
from .forms import ClientForm, ProjectForm

@login_required
def projects_view(request):
    client_form = ClientForm()
    project_form = ProjectForm()

    if request.method == 'POST':
        if 'save_client' in request.POST:
            client_form = ClientForm(request.POST)
            if client_form.is_valid():
                client_form.save()
                return redirect('projects')  # ✅ Correct name

        if 'save_project' in request.POST:
            project_form = ProjectForm(request.POST)
            if project_form.is_valid():
                project_form.save()
                return redirect('projects')  # ✅ Correct name

    clients = Client.objects.all()
    projects = Project.objects.all()
    
    return render(request, 'projects/projects.html', {
        'clients': clients,
        'projects': projects,
        'client_form': client_form,
        'project_form': project_form,
    })
