from django.shortcuts import render
from .models import ProjectReportMV
from decimal import Decimal

def reports_view(request):
    report_type = request.GET.get('report_type', 'project_cost_tracking')
    report_data = []
    table_headers = []
    template_name = 'reports/reports_table_project_cost.html'

    if report_type == 'project_cost_tracking':
        queryset = ProjectReportMV.objects.all()
        report_data_list = []
        for item in queryset:
            data = {
                # 'project_code': item.project_code,
                'client_name': item.client_name,
                'project_name': item.project_name,
                'project_status': item.project_status,
                'total_budget': item.total_budget if item.total_budget is not None else Decimal('0.00'),
                'cost_spent': item.cost_spent if item.cost_spent is not None else Decimal('0.00'),
                'remaining_budget': item.remaining_budget if item.remaining_budget is not None else Decimal('0.00'),
                'percent_budget_used': item.percent_budget_used if item.percent_budget_used is not None else Decimal('0.00'),

                'allotted_hours': item.allotted_hours if item.allotted_hours is not None else Decimal('0.00'),
                'worked_hours': item.worked_hours if item.worked_hours is not None else Decimal('0.00'),
                'remaining_hours': item.remaining_hours if item.remaining_hours is not None else Decimal('0.00'),                
                'percent_time_used': item.percent_time_used if item.percent_time_used is not None else Decimal('0.00'),
                'num_resources_assigned': item.num_resources_assigned if item.num_resources_assigned is not None else 0,
                'project_lead_name': item.project_lead_name,
                # 'delivery_head_name': item.delivery_head_name,
            }
            # Format decimal fields to 2 decimal places as strings for consistent display
            for key in ['total_budget', 'allotted_hours', 'worked_hours', 'remaining_hours',
                        'cost_spent', 'remaining_budget', 'percent_budget_used', 'percent_time_used']:
                if isinstance(data[key], Decimal):
                    data[key] = "{:.2f}".format(data[key])
                elif isinstance(data[key], (int, float)):
                    data[key] = "{:.2f}".format(Decimal(str(data[key])))
                else:
                    data[key] = '0.00' # Default if None or other unexpected type

            report_data_list.append(data)
        report_data = report_data_list
        table_headers = [
            {'title': 'Client Name', 'data': 'client_name'},
            {'title': 'Project Name', 'data': 'project_name'},
            {'title': 'Status', 'data': 'project_status'},
            {'title': 'Total Budget', 'data': 'total_budget'},
            {'title': 'Cost Spent', 'data': 'cost_spent'},
            {'title': 'Remaining Budget', 'data': 'remaining_budget'},
            {'title': '% Budget Used', 'data': 'percent_budget_used'},
            {'title': 'Allotted Hours', 'data': 'allotted_hours'},
            {'title': 'Worked Hours', 'data': 'worked_hours'},
            {'title': 'Remaining Hours', 'data': 'remaining_hours'},
            {'title': '% Time Used', 'data': 'percent_time_used'},
            {'title': '# Resources', 'data': 'num_resources_assigned'},
            {'title': 'Project Lead', 'data': 'project_lead_name'},
        ]
        template_name = 'reports/reports_table_project_cost.html'

    context = {
        'report_type': report_type,
        'report_data': report_data,
        'table_headers': table_headers,
        'template_name': template_name,
    }
    return render(request, 'reports/reports.html', context)


# # Completely working one 
# from django.shortcuts import render
# from django.db.models import Sum, F, Q
# from core.models import Timesheet, Project, Resource, Department

# def reports_view(request):
#     return render(request, 'reports/reports.html')

# def reports_partial_view(request):
#     report_type = request.GET.get('report_type', 'project')

#     context = {}

#     if report_type == 'project':
#         data = []
#         projects = Project.objects.select_related('client').all()
#         for project in projects:
#             timesheets = Timesheet.objects.filter(project=project).select_related('resource')
#             total_hours = sum([t.hours for t in timesheets])
#             total_cost = sum([t.hours * (t.resource.hourly_rate or 0) for t in timesheets])
#             utilization = (total_cost / project.budget * 100) if project.budget else 0

#             data.append({
#                 'client': project.client.name,
#                 'project': project.name,
#                 'budget': project.budget,
#                 'hours': total_hours,
#                 'cost': total_cost,
#                 'utilization': round(utilization, 2),
#             })
#         context['project_cost_data'] = data
#         return render(request, 'reports/project_report.html', context)

#     elif report_type == 'department':
#         data = []
#         departments = Department.objects.prefetch_related('resource_set__assigned_projects')
#         for dept in departments:
#             resources = dept.resource_set.all()
#             projects = Project.objects.filter(resource__in=resources).distinct()
#             timesheets = Timesheet.objects.filter(resource__in=resources)

#             total_hours = sum(t.hours for t in timesheets)
#             total_cost = sum(t.hours * (t.resource.hourly_rate or 0) for t in timesheets)
#             total_budget = sum(p.budget for p in projects)
#             budget_utilization = (total_cost / total_budget * 100) if total_budget else 0

#             data.append({
#                 'department': dept.name,
#                 'total_projects': projects.count(),
#                 'total_budget': total_budget,
#                 'total_hours': total_hours,
#                 'cost_spent': total_cost,
#                 'budget_utilization': round(budget_utilization, 2),
#                 'assigned_resources': resources.count()
#             })
#         context['department_data'] = data
#         return render(request, 'reports/department_report.html', context)

#     elif report_type == 'employee':
#         data = []
#         resources = Resource.objects.filter(status='Active').prefetch_related('timesheet_set', 'assigned_projects')
#         for resource in resources:
#             timesheets = resource.timesheet_set.all()
#             total_hours = sum(t.hours for t in timesheets)
#             working_days = timesheets.values('date').distinct().count()
#             billable_ts = timesheets.filter(project__commercial='Billable')
#             non_billable_ts = timesheets.filter(project__commercial='Non-Billable')
#             billable_hours = sum(t.hours for t in billable_ts)
#             non_billable_hours = sum(t.hours for t in non_billable_ts)

#             utilization_pct = (total_hours / (working_days * 8) * 100) if working_days else 0
#             billable_cost = sum(t.hours * (t.resource.hourly_rate or 0) for t in billable_ts)
#             non_billable_cost = sum(t.hours * (t.resource.hourly_rate or 0) for t in non_billable_ts)

#             data.append({
#                 'emp_id': resource.emp_id,
#                 'name': resource.name,
#                 'total_hours': total_hours,
#                 'billable_hours': billable_hours,
#                 'non_billable_hours': non_billable_hours,
#                 'utilization': round(utilization_pct, 2),
#                 'billable_cost': billable_cost,
#                 'non_billable_cost': non_billable_cost,
#             })
#         context['employee_data'] = data
#         return render(request, 'reports/employee_report.html', context)
