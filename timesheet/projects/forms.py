from django import forms
from core.models import Client, Project, ProjectTaskAssignment, Task, SubTask

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client', 'status', 'commercial', 'type', 'project_lead', 'delivery_head', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'commercial': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'project_lead': forms.Select(attrs={'class': 'form-control'}),
            'delivery_head': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProjectTaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = ProjectTaskAssignment
        fields = ['project', 'task', 'subtask', 'allotted_hours']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            # 'task': forms.Select(attrs={'class': 'form-select', 'hx-get': '/get-subtasks/', 'hx-target': '#id_subtask', 'hx-trigger': 'change'}),
            'task': forms.Select(attrs={'class': 'form-select'}),
            # 'subtask': forms.Select(attrs={'class': 'form-select', 'id': 'id_subtask'}),
            'subtask': forms.Select(attrs={'class': 'form-select'}),
            'allotted_hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }