from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from core.models import Resource, Project, Timesheet, Department

from datetime import timedelta, date
from collections import defaultdict
from decimal import Decimal
import json
from django.utils.safestring import mark_safe

def dashboard_view(request):
    # Scorecards
    total_resources = Resource.objects.filter(status='Active').count()
    total_projects = Project.objects.count()
    total_hours = Timesheet.objects.aggregate(total=Sum('hours'))['total'] or 0

    timesheets = Timesheet.objects.annotate(
        cost=ExpressionWrapper(F('hours') * F('resource__hourly_rate'), output_field=DecimalField())
    )
    total_cost = sum(t.cost or 0 for t in timesheets)

    # Project-wise Cost Utilization
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
            'red' if utilization > 90
            else 'yellow' if utilization >= 75
            else 'green'
        )
        project_data.append({'project': project.name, 'utilization': utilization, 'color': color})
        project_labels.append(project.name)
        project_utilization.append(utilization)
        project_colors.append(color)

    # Department-wise Cost
    dept_cost = defaultdict(lambda: Decimal('0.0'))
    for t in timesheets:
        dept = t.resource.department.name if t.resource.department else 'Unknown'
        dept_cost[dept] += t.cost or 0

    dept_cost_labels = list(dept_cost.keys())
    dept_cost_values = [float(value) for value in dept_cost.values()]

    # Projects Nearing Budget
    nearing_budget = [p for p in project_data if p['utilization'] > 85]

    # Project Resource Utilization
    res_util_labels = []
    res_util_values = []
    for project in Project.objects.all():
        team = Resource.objects.filter(assigned_projects=project)
        total_available = team.count() * 8  # Assuming 1 day
        total_billable = Timesheet.objects.filter(project=project).aggregate(total=Sum('hours'))['total'] or 0
        percent_decimal = (total_billable / total_available * 100) if total_available else Decimal('0.00')
        percent = round(float(percent_decimal), 2) if total_available else 0
        res_util_labels.append(project.name)
        res_util_values.append(percent)

    # Weekly Logged-in Hours
    today = date.today()
    weeks = [(today - timedelta(days=7 * i)) for i in range(5)][::-1]
    weekly_labels = []
    weekly_values = []

    for start_date in weeks:
        end_date = start_date + timedelta(days=6)
        total_decimal = Timesheet.objects.filter(date__range=(start_date, end_date)).aggregate(Sum('hours'))['hours__sum'] or Decimal('0.00')
        weekly_labels.append(start_date.strftime("%b %d"))
        weekly_values.append(float(total_decimal))  # Convert Decimal to float
    metrics = [
        ("Resources", total_resources),
        ("Projects", total_projects),
        ("Hours Worked", total_hours),
        ("Cost Spent", round(total_cost, 2)),
    ]

    context = {
        'metrics': metrics,
        'project_labels': mark_safe(json.dumps(project_labels)),
        'project_utilization': mark_safe(json.dumps(project_utilization)),
        'project_colors': mark_safe(json.dumps(project_colors)),
        'dept_cost_labels': mark_safe(json.dumps(list(dict(dept_cost).keys()))),
        'dept_cost_values': mark_safe(json.dumps([float(v) for v in dict(dept_cost).values()])),
        'nearing_budget': nearing_budget,
        'res_util_labels': mark_safe(json.dumps(res_util_labels)),
        'res_util_values': mark_safe(json.dumps(res_util_values)),
        'weekly_labels': mark_safe(json.dumps(weekly_labels)),
        'weekly_values': mark_safe(json.dumps(weekly_values)),
    }



    return render(request, 'dashboard/dashboard.html', context)
