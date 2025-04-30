from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from core.models import Category, Task, SubTask
from .forms import CategoryForm, TaskForm, SubTaskForm

# Main task page (returns full or partial based on request)
def task_page(request):
    categories = Category.objects.prefetch_related("tasks__subtasks").all()
    if request.htmx:
        return render(request, "taskmanager/partials/task_table.html", {"categories": categories})
    return render(request, "taskmanager/task_page.html", {"categories": categories})

# --------------------------
# CATEGORY VIEWS
# --------------------------

def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return task_page(request)  # Reload table via HTMX
    else:
        form = CategoryForm()
    return render(request, "taskmanager/partials/add_category_form.html", {"form": form})

def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return task_page(request)
    else:
        form = CategoryForm(instance=category)
    return render(request, "taskmanager/partials/edit_category_form.html", {"form": form, "category": category})

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return task_page(request)

# --------------------------
# TASK VIEWS
# --------------------------

def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return task_page(request)
    else:
        form = TaskForm()
    return render(request, "taskmanager/partials/add_task_form.html", {"form": form})

def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return task_page(request)
    else:
        form = TaskForm(instance=task)
    return render(request, "taskmanager/partials/edit_task_form.html", {"form": form, "task": task})

def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return task_page(request)

# --------------------------
# SUBTASK VIEWS
# --------------------------

def add_subtask(request):
    if request.method == "POST":
        form = SubTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return task_page(request)
    else:
        form = SubTaskForm()
    return render(request, "taskmanager/partials/add_subtask_form.html", {"form": form})

def edit_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    if request.method == "POST":
        form = SubTaskForm(request.POST, instance=subtask)
        if form.is_valid():
            form.save()
            return task_page(request)
    else:
        form = SubTaskForm(instance=subtask)
    return render(request, "taskmanager/partials/edit_subtask_form.html", {"form": form, "subtask": subtask})

def delete_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    subtask.delete()
    return task_page(request)
