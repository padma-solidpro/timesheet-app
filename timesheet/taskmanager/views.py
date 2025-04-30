from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from core.models import Category, Task, SubTask
from .forms import CategoryForm, TaskForm, SubTaskForm
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

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

# --------------------------
# CASCADING TASK FORM VIEWS (HTMX)
# --------------------------

def load_tasks_for_category(request):
    category_id = request.GET.get("category")
    if not category_id or category_id == "__new__":
        return render(request, "taskmanager/partials/task_dropdown.html", {"tasks": []})
    try:
        category_id = int(category_id)
    except ValueError:
        return render(request, "taskmanager/partials/task_dropdown.html", {"tasks": []})

    tasks = Task.objects.filter(category_id=category_id)
    return render(request, "taskmanager/partials/task_dropdown.html", {"tasks": tasks})

@csrf_exempt
def save_full_task(request):
    if request.method == "POST":
        category_id = request.POST.get("category")
        new_category_name = request.POST.get("new_category")
        task_id = request.POST.get("task")
        new_task_name = request.POST.get("new_task")
        subtasks = request.POST.getlist("subtasks")

        # Handle category
        if category_id == "__new__" and new_category_name:
            category = Category.objects.create(name=new_category_name)
        else:
            try:
                category = get_object_or_404(Category, id=int(category_id))
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid category ID"}, status=400)

        # Handle task
        if task_id == "__new__" and new_task_name:
            task = Task.objects.create(name=new_task_name, category=category)
        else:
            try:
                task = get_object_or_404(Task, id=int(task_id))
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid task ID"}, status=400)

        # Handle subtasks
        for name in subtasks:
            if name.strip():
                SubTask.objects.create(name=name.strip(), task=task)

        html = render_to_string("taskmanager/partials/task_table.html", {
            "categories": Category.objects.prefetch_related("tasks__subtasks").all()
        })
        return HttpResponse(html + "<script>window.dispatchEvent(new Event('closeModal'));</script>")

    return JsonResponse({"error": "Invalid request method"}, status=400)

# View to serve the cascading form modal content
def cascading_task_form(request):
    categories = Category.objects.all()
    return render(request, "taskmanager/partials/cascading_task_form.html", {"categories": categories})