from django import forms
from core.models import Category, Task, SubTask

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'})
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Name'}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }

class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ['name', 'task']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subtask Name'}),
            'task': forms.Select(attrs={'class': 'form-select'})
        }
