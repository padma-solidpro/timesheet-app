from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q
from django.utils.safestring import mark_safe
from core.models import Resource, Timesheet, ProjectTaskAssignment, Project, Department
from datetime import date, timedelta, datetime
from decimal import Decimal
from collections import defaultdict
from django.db.models.functions import Coalesce
from django.utils import timezone
import json


def calculate_available_hours_from_logs(resource, start_date, end_date):
    logged_dates = Timesheet.objects.filter(
        resource=resource,
        date__gte=start_date,
        date__lte=end_date
    ).values_list('date', flat=True).distinct()

    available_hours = len(logged_dates) * 8
    return available_hours

def dashboard_view(request):
    user = request.user
    resource = Resource.objects.filter(user=user).first()

    if not resource:
        return render(request, 'dashboard/error.html', {'error': 'Resource not found'})

    role = resource.role
    context = {'role': role}
    access_level = resource.role.access_level if resource.role else 0
    # ========== RESOURCE DASHBOARD (SE / Trainee) ==========
    if access_level <= 2:
        assigned_projects = resource.assigned_projects.all()
        total_assigned_projects = assigned_projects.count()

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        total_hours = Timesheet.objects.filter(
            resource=resource,
            date__gte=start_of_week,
            date__lte=end_of_week
        ).aggregate(
            total=Coalesce(Sum('hours', output_field=DecimalField()), 0, output_field=DecimalField())
        )['total']

        leave_hours = Timesheet.objects.filter(
            resource=resource,
            project__name='Leave',
            date__gte=start_of_week,
            date__lte=end_of_week
        ).aggregate(
            leave_sum=Coalesce(Sum('hours', output_field=DecimalField()), 0, output_field=DecimalField())
        )['leave_sum']

        productive_hours = total_hours - leave_hours
        available_hours = calculate_available_hours_from_logs(resource, start_of_week, end_of_week)
        utilization_percentage = (productive_hours / available_hours) * 100 if available_hours > 0 else 0.0

        project_hours = Timesheet.objects.filter(resource=resource).values('project__name') \
            .annotate(total=Sum('hours')).order_by('-total')
        project_labels = [p['project__name'] for p in project_hours]
        project_values = [float(p['total']) for p in project_hours]

        task_hours = Timesheet.objects.filter(resource=resource, task__isnull=False) \
            .values('task__name') \
            .annotate(total=Sum('hours')) \
            .order_by('-total')

        task_labels = [t['task__name'] for t in task_hours]
        task_values = [float(t['total']) for t in task_hours]

        billable_hours = Timesheet.objects.filter(resource=resource, project__commercial='Billable').aggregate(Sum('hours'))['hours__sum'] or 0
        non_billable_hours = Timesheet.objects.filter(resource=resource, project__commercial='Non-Billable').aggregate(Sum('hours'))['hours__sum'] or 0

        today = date.today()
        weekly_labels = [f"Week {i}" for i in range(1, 6)]
        weekly_values = []
        for i in range(5):
            start = today - timedelta(days=(7 * (4 - i)))
            end = start + timedelta(days=6)
            hours = Timesheet.objects.filter(resource=resource, date__range=(start, end)) \
                .aggregate(Sum('hours'))['hours__sum'] or 0
            weekly_values.append(int(hours))

        monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_values = []
        for m in range(1, 13):
            hours = Timesheet.objects.filter(resource=resource, date__month=m) \
                .aggregate(Sum('hours'))['hours__sum'] or 0
            monthly_values.append(int(hours))

        task_logged = Timesheet.objects.filter(resource=resource) \
            .values('task_description').annotate(total=Sum('hours'))

        task_allotted = ProjectTaskAssignment.objects.filter(project__in=assigned_projects)

        task_comparison = []
        for t in task_allotted:
            label = f"{t.task.name} ({t.project.name})"
            allotted = float(t.allotted_hours)
            logged = next((float(l['total']) for l in task_logged if l['task_description'] == label), 0.0)
            task_comparison.append({'task': label, 'allotted': allotted, 'logged': logged})

        context.update({
            'total_assigned_projects': total_assigned_projects,
            'total_hours': int(total_hours),
            'utilization': float(utilization_percentage),
            'project_hours_labels': mark_safe(json.dumps(project_labels)),
            'project_hours_values': mark_safe(json.dumps(project_values)),
            'weekly_labels': mark_safe(json.dumps(weekly_labels)),
            'weekly_values': mark_safe(json.dumps(weekly_values)),
            'monthly_labels': mark_safe(json.dumps(monthly_labels)),
            'monthly_values': mark_safe(json.dumps(monthly_values)),
            'task_comparison': task_comparison,
            'task_hours_labels': mark_safe(json.dumps(task_labels)),
            'task_hours_values': mark_safe(json.dumps(task_values)),
            'billable_hours': float(billable_hours),
            'non_billable_hours': float(non_billable_hours)
        })

        return render(request, 'dashboard/resource_dashboard.html', context)

    # ========== PROJECT LEAD DASHBOARD ==========
    elif access_level == 3:
        projects = Project.objects.filter(project_lead=resource)
        all_projects = projects
    elif access_level == 4:
        projects = Project.objects.filter(delivery_head=resource)
        all_projects = projects
    else:
        return render(request, 'dashboard/unauthorized.html')

    # Get the seleced project and date_range
    selected_project = request.GET.get('project')
    if selected_project:
        projects = projects.filter(id=selected_project)
    # selected_employee = request.GET.get('employee') will reuse it when needed

    context = {}

    total_resources = Resource.objects.filter(status='Active', assigned_projects__in=projects).count()
    employees = Resource.objects.filter(status='Active', reporting_to=resource)
    print("Employees: ", employees)
    total_projects = projects.count()
    active_projects = projects.filter(status='Active').count()
    closed_projects = projects.filter(status='Closed').count()

    today = timezone.now().date()
    end_date = today
    start_date = end_date - timedelta(days=7)
    prev_start = start_date - timedelta(days=7)
    prev_end = start_date - timedelta(days=1)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else today - timedelta(days=7)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today
    except ValueError:
        start_date = today - timedelta(days=7)
        end_date = today

    timesheets = Timesheet.objects.filter(project__in=projects).annotate(
        cost=ExpressionWrapper(F('hours') * F('resource__hourly_rate'), output_field=DecimalField())
    )
    this_week_hours = Timesheet.objects.filter(project__in=projects, date__range=(start_date, end_date)).aggregate(Sum('hours'))['hours__sum'] or 0
    prev_week_hours = Timesheet.objects.filter(project__in=projects, date__range=(prev_start, prev_end)).aggregate(Sum('hours'))['hours__sum'] or 0
    delta_hours = this_week_hours - prev_week_hours

    if delta_hours > 0:
        direction = 'up'
        change = f"+{delta_hours:.1f} hrs"
    elif delta_hours < 0:
        direction = 'down'
        change = f"{delta_hours:.1f} hrs"
    else:
        direction = ''
        change = "0 hrs"
        
    this_week_cost = sum(
        t.hours * (t.resource.hourly_rate or 0)
        for t in Timesheet.objects.filter(project__in=projects, date__range=(start_date, end_date))
    )
    prev_week_cost = sum(
        t.hours * (t.resource.hourly_rate or 0)
        for t in Timesheet.objects.filter(project__in=projects, date__range=(prev_start, prev_end))
    )
    delta_cost = this_week_cost - prev_week_cost

    total_hours = Timesheet.objects.filter(project__in=projects).aggregate(total=Sum('hours'))['total'] or 0
    total_cost = sum(t.cost or 0 for t in timesheets)

    project_labels_cost, project_utilization_values, project_colors_cost = [], [], []
    project_budget, project_spent = [], []
    project_data = []

    for p in projects:
        spent = sum(
            t.hours * (t.resource.hourly_rate or 0)
            for t in Timesheet.objects.filter(project=p, date__range=(start_date, end_date))
        )
        utilization = round((spent / p.budget) * 100, 2) if p.budget else 0
        color = 'red' if utilization > 100 else 'orange' if utilization >= 90 else 'green'

        project_labels_cost.append(p.name)
        project_utilization_values.append(utilization)
        project_colors_cost.append(color)
        project_budget.append(float(p.budget or 0))
        project_spent.append(float(spent))
        project_data.append({'project': p.name, 'utilization': utilization, 'color': color})

    budget_status = [p for p in project_data if p['utilization'] >= 90]

    dept_cost = defaultdict(lambda: Decimal('0.0'))
    for t in timesheets:
        dept = t.resource.department.name if t.resource.department else "Unknown"
        dept_cost[dept] += t.cost or 0

    dept_cost_labels = list(dept_cost.keys())
    dept_cost_values = [float(x) for x in dept_cost.values()]

    res_util_labels, res_util_values = [], []
    for p in projects:
        team = Resource.objects.filter(assigned_projects=p, status='Active')
        available_hours = team.count() * 8 * (end_date - start_date).days if (end_date - start_date).days > 0 else team.count() * 8
        worked_hours = Timesheet.objects.filter(project=p, date__range=(start_date, end_date)).aggregate(Sum('hours'))['hours__sum'] or 0
        utilization = (worked_hours / available_hours * 100) if available_hours else 0
        res_util_labels.append(p.name)
        res_util_values.append(round(utilization, 2))

    daily_trend = []
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    for day in date_range:
        daily_hours = Timesheet.objects.filter(project__in=projects, date=day).aggregate(Sum('hours'))['hours__sum'] or 0
        daily_trend.append({'date': day.strftime('%Y-%m-%d'), 'hours': float(daily_hours)})
    
    weekly_trend = []
    week_start = start_date - timedelta(days=start_date.weekday())
    week_end = end_date + timedelta(days=(6 - end_date.weekday()))
    for i in range(0, (week_end - week_start).days + 1, 7):
        start = week_start + timedelta(days=i)
        end = start + timedelta(days=6)
        weekly_hours = Timesheet.objects.filter(project__in=projects, date__range=(start, end)).aggregate(Sum('hours'))['hours__sum'] or 0
        weekly_trend.append({'start': start.strftime('%Y-%m-%d'), 'end': end.strftime('%Y-%m-%d'), 'hours': float(weekly_hours)})

    monthly_trend = []
    month_start = date(start_date.year, start_date.month, 1)
    month_end = date(end_date.year, end_date.month, 1)
    while month_start <= month_end:
        next_month = month_start.replace(day=28) + timedelta(days=4)
        current_month_end = next_month - timedelta(days=next_month.day)
        monthly_hours = Timesheet.objects.filter(project__in=projects, date__range=(month_start, current_month_end)).aggregate(Sum('hours'))['hours__sum'] or 0
        monthly_trend.append({'month': month_start.strftime('%Y-%m'), 'hours': float(monthly_hours)})
        month_start = current_month_end + timedelta(days=1)

    project_hours_report = []
    task_hours_report = []
    project_task_assignments = ProjectTaskAssignment.objects.filter(project__in=projects)

    project_hours_data = Timesheet.objects.filter(project__in=projects, date__range=(start_date, end_date)).values('project__name').annotate(worked=Sum('hours')).order_by('-worked')
    for item in project_hours_data:
        allotted = project_task_assignments.filter(project__name=item['project__name']) \
    .aggregate(total=Coalesce(Sum('allotted_hours', output_field=DecimalField()), Decimal(0)))['total'] or Decimal(0)

        project_hours_report.append({'name': item['project__name'], 'worked': float(item['worked']), 'allotted': float(allotted)})

    task_hours_data = Timesheet.objects.filter(project__in=projects, date__range=(start_date, end_date), task__isnull=False).values('task__name').annotate(worked=Sum('hours')).order_by('-worked')

    for item in task_hours_data:
        allotted = project_task_assignments.filter(task__name=item['task__name']).aggregate(total=Coalesce(Sum('allotted_hours',output_field=DecimalField()), Decimal(0)))['total'] or Decimal(0)
        task_hours_report.append({'name': item['task__name'], 'worked': float(item['worked']), 'allotted': float(allotted)})

    billable_hours = Timesheet.objects.filter(resource=resource, project__commercial='Billable').aggregate(Sum('hours'))['hours__sum'] or 0
    non_billable_hours = Timesheet.objects.filter(resource=resource, project__commercial='Non-Billable').aggregate(Sum('hours'))['hours__sum'] or 0

    timesheet_summary = []
    week_start_date = start_date - timedelta(days=start_date.weekday())
    for r in Resource.objects.filter(assigned_projects__in=projects, status='Active').distinct():
        submitted = Timesheet.objects.filter(resource=r, date__range=(start_date, end_date)).exists()
        logged_days = Timesheet.objects.filter(resource=r, date__range=(start_date, end_date)).values_list('date', flat=True).distinct()
        expected_days = set(start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)).weekday() < 5)
        missed_log = sorted(list(expected_days - set(logged_days)))
        pending_approval = Timesheet.objects.filter(resource=r, status='Pending', date__range=(start_date, end_date)).count()
        timesheet_summary.append({
            'resource': r.name,
            'submitted': submitted,
            'missed_log': [d.strftime('%Y-%m-%d') for d in missed_log],
            'approval_pending': pending_approval,
            'week_start': week_start_date.strftime('%Y-%m-%d')
        })

    absentees = []
    for r in Resource.objects.filter(assigned_projects__in=projects, status="Active").distinct():
        submitted = Timesheet.objects.filter(resource=r, date__range=(start_date, end_date)).exists()
        if not submitted:
            absentees.append(r.name)
    
    approval_counter = defaultdict(lambda: {"count": 0, "employees": []})
    pending_approvals = Timesheet.objects.filter(status='Pending').order_by('-date')
    for approval in pending_approvals:
      readable_date = format(approval.date, 'd M')
      approval_counter[readable_date]["count"] += 1
      approval_counter[readable_date]["employees"].append(approval.resource.name)

    context.update({
        "metrics": [
            ("Projects", total_projects),
            ("Resources", total_resources),
            ("Active Projects", active_projects),
            # ("Closed Projects", closed_projects),
            ("Hours Worked", f"{this_week_hours:.1f} hrs", change, direction),
            ("Cost Spent", f"{round(this_week_cost, 2)} ({delta_cost:+})"),
            ("Absents", len(absentees)),
        ],
        "projects": all_projects,
        "employees": employees,
        "project_labels_cost": mark_safe(json.dumps(project_labels_cost)),
        "project_utilization_values": mark_safe(json.dumps([float(x) for x in project_utilization_values])),
        "project_colors_cost": mark_safe(json.dumps(project_colors_cost)),
        "project_budget": mark_safe(json.dumps([float(x) for x in project_budget])),
        "project_spent": mark_safe(json.dumps([float(x) for x in project_spent])),
        "dept_cost_labels": mark_safe(json.dumps(dept_cost_labels)),
        "dept_cost_values": mark_safe(json.dumps([float(x) for x in dept_cost_values])),
        "res_util_labels": mark_safe(json.dumps(res_util_labels)),
        "res_util_values": mark_safe(json.dumps([float(x) for x in res_util_values])),
        "daily_labels": mark_safe(json.dumps([item['date'] for item in daily_trend])),
        "daily_values": mark_safe(json.dumps([item['hours'] for item in daily_trend])),
        "weekly_labels_trend": mark_safe(json.dumps([f"{item['start']} - {item['end']}" for item in weekly_trend])),
        "weekly_values_trend": mark_safe(json.dumps([item['hours'] for item in weekly_trend])),
        "monthly_labels_trend": mark_safe(json.dumps([item['month'] for item in monthly_trend])),
        "monthly_values_trend": mark_safe(json.dumps([item['hours'] for item in monthly_trend])),
        "nearing_budget": budget_status,
        "timesheet_summary": timesheet_summary,
        "start_date": start_date,
        "end_date": end_date,
        "absentees": absentees,
        "project_hours_labels": mark_safe(json.dumps([item['name'] for item in project_hours_report])),
        "project_hours_worked": mark_safe(json.dumps([item['worked'] for item in project_hours_report])),
        "project_hours_allotted": mark_safe(json.dumps([item['allotted'] for item in project_hours_report])),
        "task_hours_labels": mark_safe(json.dumps([item['name'] for item in task_hours_report])),
        "task_hours_worked": mark_safe(json.dumps([item['worked'] for item in task_hours_report])),
        "task_hours_allotted": mark_safe(json.dumps([item['allotted'] for item in task_hours_report])),
        'billable_hours': float(billable_hours),
        'non_billable_hours': float(non_billable_hours),
        "project_labels_cost": mark_safe(json.dumps(project_labels_cost)),
        "project_budget": mark_safe(json.dumps(project_budget)),
        "project_spent": mark_safe(json.dumps(project_spent)),
        "pending_approvals": pending_approvals,
        "task_utilization_values": mark_safe(json.dumps([round((t['worked'] / t['allotted']) * 100, 2) if t['allotted'] > 0 else 0 for t in task_hours_report]))

    })

    return render(request, "dashboard/dashboard.html", context)