from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from core.models import Project, Task, SubTask, ProjectTaskAssignment, Timesheet, Resource, Role
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest
from .forms import TimesheetForm, ApprovalForm
from django.contrib import messages


@login_required
def timesheet_view(request):
    resource = request.user.resource
    role = resource.role
    role_name = role.name
    access_level = role.access_level

    today = timezone.now().date()
    assigned_projects = resource.assigned_projects.all()
    self_records = Timesheet.objects.filter(resource=resource, status__in=["Pending", "Rejected"]).order_by('-date')
    approval_records = Timesheet.objects.none()  # Default

    filter_param = request.GET.get('filter')
    # Access Level 1 & 2: Only their own timesheets
    if access_level in [1, 2]:
        pass  # self_records already populated

    # Access Level 3: Project Lead
    elif access_level == 3:
        projects = Project.objects.filter(project_lead=resource)

        self_records = Timesheet.objects.filter(
            project__in=projects, resource=resource, status__in=["Pending", "Rejected"]
        ).order_by('-date')

        approval_records = Timesheet.objects.filter(
            project__in=projects,
            status__in=["Pending", "Rejected"]
        ).exclude(resource=resource) \
        .filter(resource__role__access_level__lt=3) \
        .order_by('-date')

    # Access Level 4: Delivery Lead
    elif access_level == 4:
        projects = Project.objects.filter(delivery_head=resource)

        self_records = Timesheet.objects.filter(
            project__in=projects, resource=resource, status__in=["Pending", "Rejected"]
        ).order_by('-date')  # may be empty

        approval_records = Timesheet.objects.filter(
            project__in=projects,
            status__in=["Pending", "Rejected"]
        ).exclude(resource=resource) \
        .filter(resource__role__access_level=3) \
        .order_by('-date')

    # CEO or Superuser
    elif request.user.is_superuser or role_name.lower() == "ceo":
        self_records = Timesheet.objects.all().order_by('-date')
        approval_records = Timesheet.objects.filter(status='Pending').order_by('-date')

    context = {
        'timesheet_entries': self_records,
        'approval_records': approval_records,
        'assigned_projects': assigned_projects,
        'today': today,
        'role': role_name,
        'filter': filter_param,
        'show_approval_tab': access_level >= 3,
        'aprv_has_data': bool(approval_records),
        'slef_has_data': bool(self_records),
    }

    return render(request, 'usertimesheet/timesheet.html', context)

# Submit all rows in one go
def submit_timesheet_entries(request):
    if request.method == "POST":
        date = request.POST.get("date")
        rows = [key.split('_')[1] for key in request.POST if key.startswith("project_")]
        saved = 0

        resource = get_object_or_404(Resource, user=request.user)  # ✅ Fix here
        existing_entries = Timesheet.objects.filter(resource=resource, date=date)
        if Timesheet.objects.filter(resource=resource, date=date).exists():
            context = {
                "duplicate_entry": True,
                "assigned_projects": resource.assigned_projects.all(),  # if needed for re-render
                "timesheet_entries": Timesheet.objects.filter(resource=resource).order_by('-date')  # optional
            }
            return render(request, "usertimesheet/timesheet.html", context)
        
        for index in set(rows):
            project_id = request.POST.get(f"project_{index}")
            task_id = request.POST.get(f"task_{index}")
            subtask_id = request.POST.get(f"subtask_{index}")
            desc = request.POST.get(f"description_{index}")
            hours = request.POST.get(f"hours_{index}")

            if project_id and hours:
                project = get_object_or_404(Project, id=project_id)  # Fetch the project by ID
                task = get_object_or_404(Task, id=task_id) if task_id else None
                subtask = get_object_or_404(SubTask, id=subtask_id) if subtask_id else None

                Timesheet.objects.create(
                    resource=resource,
                    date=date,
                    project=project,  # Use the actual `project` object, not the `project_id`
                    task=task,
                    subtask=subtask,
                    task_description=desc,
                    hours=hours,
                    status='Pending'
                )
                saved += 1

        return redirect("usertimesheet")

@login_required
def get_project_tasks(request):
    index = request.GET.get('index')
    project_id = request.GET.get(f'project_{index}') or request.GET.get('project')
    selected_id = request.GET.get('selected_id')

    tasks = []
    if project_id:
        task_ids = ProjectTaskAssignment.objects.filter(project_id=project_id).values_list('task_id', flat=True)
        tasks = Task.objects.filter(id__in=task_ids).distinct().values_list('id', 'name')

    return render(request, 'usertimesheet/partials/task_options.html', {
        'tasks': tasks,
        'selected_id': selected_id
    })

@login_required
def get_task_subtasks(request):
    index = request.GET.get('index')
    task_id = request.GET.get(f'task_{index}') or request.GET.get('task')
    selected_id = request.GET.get('selected_id')
    print(f"Received task_id: {task_id}")

    subtasks = []
    if task_id:
        subtasks = SubTask.objects.filter(task_id=task_id)
        print(f"Subtasks found: {subtasks.count()}")
    return render(request, 'usertimesheet/partials/subtask_options.html', {
        'subtasks': subtasks,
        'selected_id': selected_id
    })

def load_approval_form(request, pk):
    record = get_object_or_404(Timesheet, pk=pk)

    if request.method == 'POST':
        form = ApprovalForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return HttpResponse('<div hx-trigger="timesheetUpdated"></div>')  # triggers modal hide and reload
    else:
        form = ApprovalForm(instance=record)

    return render(request, 'usertimesheet/partials/approval_update_form.html', {'form': form})



@login_required
def edit_timesheet(request, pk):
    # timesheet = get_object_or_404(Timesheet, pk=pk, resource=request.user.resource)
    timesheet = get_object_or_404(Timesheet, pk=pk, resource=request.user.resource)  # Remove resource filtering for now

    if timesheet.status == 'Accepted':
        return HttpResponseForbidden("You cannot edit an approved entry.")

    if request.method == 'POST':

        form = TimesheetForm(request.POST, instance=timesheet)
        if form.is_valid():
            # form.save()
            updated_timesheet = form.save(commit=False)
            
            if updated_timesheet.status == 'Rejected':
                updated_timesheet.status = 'Pending'

            updated_timesheet.save()
            
            return HttpResponse(status=204, headers={'HX-Trigger': 'timesheetUpdated'})
            # return render(request, 'usertimesheet/partials/success_message.html')
        else:
            print(form.errors)  # <-- add this line
    else:
        form = TimesheetForm(instance=timesheet)

    project = timesheet.project
    print(project)

    # ✅ Get only tasks assigned to the selected project
    assigned_task_ids = ProjectTaskAssignment.objects.filter(
        project=project
    ).values_list('task', flat=True).distinct()

    available_tasks = Task.objects.filter(id__in=assigned_task_ids).values_list('id', 'name')

    # ✅ Get only subtasks assigned to the selected project + task
    if timesheet.task:
        assigned_subtask_ids = ProjectTaskAssignment.objects.filter(
            project=project, task=timesheet.task
        ).values_list('subtask', flat=True).distinct()
        available_subtasks = SubTask.objects.filter(id__in=assigned_subtask_ids)
    else:
        available_subtasks = SubTask.objects.none()

    return render(request, 'usertimesheet/partials/edit_timesheet_form.html', {
        'form': form,
        'timesheet': timesheet,
        # 'assigned_projects': Project.objects.all(),  # Or filter assigned to this user
        'assigned_projects': request.user.resource.assigned_projects.all(),
        'available_tasks': available_tasks,
        'available_subtasks': available_subtasks,
    })

@login_required
def timesheet_entries(request):
    timesheet_entries = Timesheet.objects.filter(resource=request.user.resource).order_by('-date')
    return render(request, 'usertimesheet/partials/timesheet_entries.html', {
        'timesheet_entries': timesheet_entries
    })

    
def add_timesheet_row(request):
    index = int(request.GET.get("index", 0))
    assigned_projects = request.user.resource.assigned_projects.all()
    context = {
        "index": index,
        "assigned_projects": assigned_projects,
    }
    return render(request, "usertimesheet/partials/timesheet_form_row.html", context)


def bulk_update_approvals(request):
    record_ids = request.POST.getlist("record_ids")
    action = request.POST.get("action")

    if not record_ids or not action:
        messages.error(request, "Please select records and an action.")
        return redirect("timesheet")  # or return the table partial again

    reviewer = request.user.resource

    for record_id in record_ids:
        try:
            record = Timesheet.objects.get(id=record_id)
            comment = request.POST.get(f"review_comment_{record_id}", "")
            record.status = action
            record.review_comment = comment
            record.reviewed_by = reviewer
            record.reviewed_on = timezone.now()
            record.save()
        except Timesheet.DoesNotExist:
            continue

    # messages.success(request, f"{len(record_ids)} record(s) updated.")

    # Return updated table
    approval_records = Timesheet.objects.filter(status__in=["Pending", "Rejected"])
    return render(request, "usertimesheet/partials/approval_entries_table.html", {
        "approval_records": approval_records
    })


# working logic of approval projects filet
# user = request.user
#     resource = get_object_or_404(Resource, user=user)
#     role_name = resource.role.name.lower()
#     today = timezone.now().date()

    

#     filter_param = request.GET.get('filter')
#     assigned_projects = resource.assigned_projects.all().distinct()

#     # Default empty querysets
#     print("Getting records of resource: ", resource)
#     self_records = Timesheet.objects.none()
#     approval_records = Timesheet.objects.none()

#     approval_roles = ['project lead', 'delivery lead', 'lead ui/ux developer']
#     show_approval_tab = role_name in approval_roles

#     # Always show self-records
#     self_records = Timesheet.objects.filter(resource=resource).order_by('-date')

#     if role_name in ["project lead", "lead ui/ux developer"]:
#         # Projects led by this user
#         projects = Project.objects.filter(project_lead=resource)

#         # Self records include all records in those projects (Project Lead can log hours too)
#         self_records = Timesheet.objects.filter(project__in=projects, resource=resource).order_by('-date')

#         # Approval: Records of employees on the PL's projects, excluding the PL's own entries
#         approval_records = Timesheet.objects.filter(
#             project__in=projects,
#             status__in=["Pending", "Rejected"]
#         ).exclude(resource=resource).order_by('-date')

#     elif role_name == "delivery lead":
#         print("Getting records of resource: ", resource)
#         projects = Project.objects.filter(delivery_head=resource)
        
#         print("[STEP 2] Delivery Lead Projects:")
#         for p in projects:
#             print(f" - {p.name}")

#         approval_records = Timesheet.objects.filter(
#             project__in=projects,
#             resource__role__access_level=3,
#             status__in=["Pending", "Rejected"]
#         ).order_by('-date')

#         print("DEBUG - Approval Records:")
#         for record in approval_records:
#             print(f"{record.date} | {record.resource.name} | {record.project.name} | {record.status}")

#     elif request.user.is_superuser or role_name == "ceo":
#         # CEO or superuser can view everything (no approval actions)
#         self_records = Timesheet.objects.all().order_by('-date')
#         approval_records = Timesheet.objects.filter(status='Pending').order_by('-date')

#     context = {
#         'timesheet_entries': self_records,
#         'approval_records': approval_records,
#         'assigned_projects': assigned_projects,
#         'today': today,
#         'role': role_name,  # fixed
#         'filter': filter_param,
#         'show_approval_tab': show_approval_tab,
#     }
