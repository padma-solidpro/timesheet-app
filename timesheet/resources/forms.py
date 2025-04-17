from django import forms
from core.models import Resource, Project

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'emp_id', 'name', 'email', 'start_date', 'end_date',
            'department', 'role', 'assigned_projects', 'reporting_to',
            'hourly_rate', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'assigned_projects': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'reporting_to': forms.Select(attrs={'class': 'form-select'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
        }