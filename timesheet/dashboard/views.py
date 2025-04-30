from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q
from django.utils.safestring import mark_safe
from core.models import Resource, Timesheet, ProjectTaskAssignment, Project
from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict
from django.db.models.functions import Coalesce
from datetime import date, timedelta

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
    context = { 'role': role }
    access_level = resource.role.access_level if resource.role else 0

    print(access_level)
    # ========== RESOURCE DASHBOARD (SE / Trainee) ==========
    if access_level <= 2:
        assigned_projects = resource.assigned_projects.all()
        total_assigned_projects = assigned_projects.count()
 
        # Total hours
        # total_hours = Timesheet.objects.filter(resource=resource).aggregate(Sum('hours'))['hours__sum'] or 0

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
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

        #utilization%
        productive_hours = total_hours - leave_hours
        available_hours = calculate_available_hours_from_logs(resource, start_of_week, end_of_week)
        if available_hours > 0:
            utilization_percentage = (productive_hours / available_hours) * 100
        else:
            utilization_percentage = 0.0
        

        # Project-wise
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

        #billable vs non-billable
        billable_hours = Timesheet.objects.filter(resource=resource, project__commercial='Billable').aggregate(Sum('hours'))['hours__sum'] or 0
        non_billable_hours = Timesheet.objects.filter(resource=resource, project__commercial='Non-Billable').aggregate(Sum('hours'))['hours__sum'] or 0

        # Weekly (5 weeks)
        today = date.today()
        weekly_labels = [f"Week {i}" for i in range(1, 6)]
        weekly_values = []
        for i in range(5):
            start = today - timedelta(days=(7 * (4 - i)))
            end = start + timedelta(days=6)
            hours = Timesheet.objects.filter(resource=resource, date__range=(start, end)) \
                .aggregate(Sum('hours'))['hours__sum'] or 0
            weekly_values.append(int(hours))
 
        # Monthly (Jan - Dec)
        monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_values = []
        for m in range(1, 13):
            hours = Timesheet.objects.filter(resource=resource, date__month=m) \
                .aggregate(Sum('hours'))['hours__sum'] or 0
            monthly_values.append(int(hours))
 
        # Task: Logged vs Allotted
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
            'utilization' : float(utilization_percentage),
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
    else:
        total_resources = Resource.objects.filter(status='Active').count()
        total_projects = Project.objects.count()
        total_hours = Timesheet.objects.aggregate(total=Sum('hours'))['total'] or 0
 
        timesheets = Timesheet.objects.annotate(
            cost=ExpressionWrapper(F('hours') * F('resource__hourly_rate'), output_field=DecimalField())
        )
        total_cost = sum(t.cost or 0 for t in timesheets)
 
        project_data = []
        project_labels = []
        project_utilization = []
        project_colors = []
 
        for project in Project.objects.all():
            cost = sum(
                t.hours * (t.resource.hourly_rate or 0)
                for t in Timesheet.objects.filter(project=project)
            )
            utilization_decimal = (cost / project.budget) * 100 if project.budget else Decimal('0.00')
            utilization = round(float(utilization_decimal), 2)
 
            color = (
                'red' if utilization > 90 else
                'yellow' if utilization >= 75 else
                'green'
            )
            project_data.append({'project': project.name, 'utilization': utilization, 'color': color})
            project_labels.append(project.name)
            project_utilization.append(utilization)
            project_colors.append(color)
 
        dept_cost = defaultdict(lambda: Decimal('0.0'))
        for t in timesheets:
            dept = t.resource.department.name if t.resource.department else 'Unknown'
            dept_cost[dept] += t.cost or 0
 
        dept_cost_labels = list(dept_cost.keys())
        dept_cost_values = [float(v) for v in dept_cost.values()]
 
        nearing_budget = [p for p in project_data if p['utilization'] > 85]
 
        res_util_labels = []
        res_util_values = []
        for project in Project.objects.all():
            team = Resource.objects.filter(assigned_projects=project)
            total_available = team.count() * 8
            total_billable = Timesheet.objects.filter(project=project).aggregate(Sum('hours'))['hours__sum'] or 0
            percent = (total_billable / total_available * 100) if total_available else 0
            res_util_labels.append(project.name)
            res_util_values.append(float(round(percent, 2)))

 
        week_labels = []
        week_values = []
        today = date.today()
        for i in range(5):
            start = today - timedelta(days=(7 * (4 - i)))
            end = start + timedelta(days=6)
            week_labels.append(start.strftime("%b %d"))
            total = Timesheet.objects.filter(date__range=(start, end)).aggregate(Sum('hours'))['hours__sum'] or 0
            week_values.append(float(total))
 
        context.update({
            'metrics': [("Resources", total_resources), ("Projects", total_projects),
                        ("Hours Worked", total_hours), ("Cost Spent", round(total_cost, 2))],
            'project_labels': mark_safe(json.dumps(project_labels)),
            'project_utilization': mark_safe(json.dumps(project_utilization)),
            'project_colors': mark_safe(json.dumps(project_colors)),
            'dept_cost_labels': mark_safe(json.dumps(dept_cost_labels)),
            'dept_cost_values': mark_safe(json.dumps(dept_cost_values)),
            'res_util_labels': mark_safe(json.dumps(res_util_labels)),
            'res_util_values': mark_safe(json.dumps(res_util_values)),
            'weekly_labels': mark_safe(json.dumps(week_labels)),
            'weekly_values': mark_safe(json.dumps(week_values)),
            'nearing_budget': nearing_budget
        })
        return render(request, 'dashboard/dashboard.html', context)