from django.shortcuts import render
from django.db.models import Sum, F, Q
from core.models import Timesheet, Project, Resource, Department

def reports_view(request):
    return render(request, 'reports/reports.html')

def reports_partial_view(request):
    report_type = request.GET.get('report_type', 'project')

    context = {}

    if report_type == 'project':
        data = []
        projects = Project.objects.select_related('client').all()
        for project in projects:
            timesheets = Timesheet.objects.filter(project=project).select_related('resource')
            total_hours = sum([t.hours for t in timesheets])
            total_cost = sum([t.hours * (t.resource.hourly_rate or 0) for t in timesheets])
            utilization = (total_cost / project.budget * 100) if project.budget else 0

            data.append({
                'client': project.client.name,
                'project': project.name,
                'budget': project.budget,
                'hours': total_hours,
                'cost': total_cost,
                'utilization': round(utilization, 2),
            })
        context['project_cost_data'] = data
        return render(request, 'reports/project_report.html', context)

    elif report_type == 'department':
        data = []
        departments = Department.objects.prefetch_related('resource_set__assigned_projects')
        for dept in departments:
            resources = dept.resource_set.all()
            projects = Project.objects.filter(resource__in=resources).distinct()
            timesheets = Timesheet.objects.filter(resource__in=resources)

            total_hours = sum(t.hours for t in timesheets)
            total_cost = sum(t.hours * (t.resource.hourly_rate or 0) for t in timesheets)
            total_budget = sum(p.budget for p in projects)
            budget_utilization = (total_cost / total_budget * 100) if total_budget else 0

            data.append({
                'department': dept.name,
                'total_projects': projects.count(),
                'total_budget': total_budget,
                'total_hours': total_hours,
                'cost_spent': total_cost,
                'budget_utilization': round(budget_utilization, 2),
                'assigned_resources': resources.count()
            })
        context['department_data'] = data
        return render(request, 'reports/department_report.html', context)

    elif report_type == 'employee':
        data = []
        resources = Resource.objects.filter(status='Active').prefetch_related('timesheet_set', 'assigned_projects')
        for resource in resources:
            timesheets = resource.timesheet_set.all()
            total_hours = sum(t.hours for t in timesheets)
            working_days = timesheets.values('date').distinct().count()
            billable_ts = timesheets.filter(project__commercial='Billable')
            non_billable_ts = timesheets.filter(project__commercial='Non-Billable')
            billable_hours = sum(t.hours for t in billable_ts)
            non_billable_hours = sum(t.hours for t in non_billable_ts)

            utilization_pct = (total_hours / (working_days * 8) * 100) if working_days else 0
            billable_cost = sum(t.hours * (t.resource.hourly_rate or 0) for t in billable_ts)
            non_billable_cost = sum(t.hours * (t.resource.hourly_rate or 0) for t in non_billable_ts)

            data.append({
                'emp_id': resource.emp_id,
                'name': resource.name,
                'total_hours': total_hours,
                'billable_hours': billable_hours,
                'non_billable_hours': non_billable_hours,
                'utilization': round(utilization_pct, 2),
                'billable_cost': billable_cost,
                'non_billable_cost': non_billable_cost,
            })
        context['employee_data'] = data
        return render(request, 'reports/employee_report.html', context)
