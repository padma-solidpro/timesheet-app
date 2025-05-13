from django.shortcuts import render
from core.models import Timesheet, Resource
from .models import ProjectReportMV, ProjectTaskTracking, EmployeeUtilizationMV
from decimal import Decimal
from datetime import date, timedelta
from collections import defaultdict
from django.db.models import Q

def reports_view(request):
    report_type = request.GET.get('report_type', 'timesheet_log_reports')
    report_data = []
    table_headers = []
    template_name = 'reports/reports_table_project_cost.html'

    resource = request.user.resource
    role = resource.role
    role_name = role.name
    access_level = role.access_level


    default_start=''
    default_end=''
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

        filterable_columns = ['Client Name', 'Project Name', 'Status']
        unsortable_columns = ['Client Name', 'Project Name', 'Status']

        template_name = 'reports/reports_table_project_cost.html'

    elif report_type == 'project_task_tracking':
        queryset = ProjectTaskTracking.objects.all()
        report_data_list = []
        for item in queryset:
            data = {
                'project_name': item.project_name,
                'task_name': item.task_name,                
                'task_status': item.task_status,
                'allotted_hours': item.allotted_hours if item.allotted_hours is not None else Decimal('0.00'),
                'worked_hours': item.worked_hours if item.worked_hours is not None else Decimal('0.00'),
                'remaining_hours': item.remaining_hours if item.remaining_hours is not None else Decimal('0.00'),   
                'cost_spent': item.cost_spent if item.cost_spent is not None else Decimal('0.00'),   
            }
            # Format decimal fields to 2 decimal places as strings for consistent display
            for key in ['allotted_hours', 'worked_hours', 'remaining_hours', 'cost_spent']:
                if isinstance(data[key], Decimal):
                    data[key] = "{:.2f}".format(data[key])
                elif isinstance(data[key], (int, float)):
                    data[key] = "{:.2f}".format(Decimal(str(data[key])))
                else:
                    data[key] = '0.00' # Default if None or other unexpected type

            report_data_list.append(data)

        report_data = report_data_list

        table_headers = [
            {'title': 'Project Name', 'data': 'project_name'},
            {'title': 'Task Name', 'data': 'task_name'},
            {'title': 'Status', 'data': 'task_status'},
            {'title': 'Allotted Hours', 'data': 'allotted_hours'},
            {'title': 'Worked Hours', 'data': 'worked_hours'},
            {'title': 'Remaining Hours', 'data': 'remaining_hours'},
            {'title': 'Cost Spent', 'data': 'cost_spent'},
        ]

        filterable_columns = ['Task Name', 'Project Name', 'Status']
        unsortable_columns = ['Task Name', 'Project Name', 'Status']
        
        template_name = 'reports/reports_table_project_cost.html'

    elif report_type == 'employee_utilization':

        # Default date range: current month
        today = date.today()
        default_start = today.replace(day=1)
        default_end = (default_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        week_filter = request.GET.get('week_filter')
        if week_filter == 'low_hours':
            # Set range to last Mon–Fri (last week)
            weekday = today.weekday()
            last_friday = today - timedelta(days=weekday + 3)  # Previous Friday
            last_monday = last_friday - timedelta(days=4)
            start_date = last_monday
            end_date = last_friday
            print('Start Date: ', start_date)
            print('End Date: ', end_date)
        else:
            # Get date range from request
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            start_date = date.fromisoformat(start_date_str) if start_date_str else default_start
            end_date = date.fromisoformat(end_date_str) if end_date_str else default_end

        qs = EmployeeUtilizationMV.objects.filter(date__range=(start_date, end_date))

        print(qs)
        # Group data by employee
        emp_data = defaultdict(lambda: {
            'emp_name': '',
            'total_hours': Decimal('0.0'),
            'billable_hours': Decimal('0.0'),
            'non_billable_hours': Decimal('0.0'),
            'leave_hours': Decimal('0.0'),
            'billable_cost': Decimal('0.0'),
            'non_billable_cost': Decimal('0.0'),
            'working_days': set(),
        })

        for row in qs:
            emp = emp_data[row.emp_id]
            emp['emp_name'] = row.emp_name
            emp['working_days'].add(row.date)

            hours_worked = Decimal(row.hours_worked or 0)
            cost_spent = Decimal(row.cost_spent or 0)

            if row.project_name.lower() == 'leave':
                emp['leave_hours'] += hours_worked
            else:
                if row.is_working_day:
                    emp['total_hours'] += hours_worked
                if row.commercial.lower() == 'billable':
                    emp['billable_hours'] += hours_worked
                    emp['billable_cost'] += cost_spent
                elif row.commercial.lower() == 'non-billable':
                    emp['non_billable_hours'] += hours_worked
                    emp['non_billable_cost'] += cost_spent

        report_data_list = []
        for emp_id, data in emp_data.items():
            total_available = Decimal(len(data['working_days']) * 8) - data['leave_hours']
            utilization = (data['billable_hours'] / total_available * 100) if total_available > 0 else Decimal('0.0')

            report_data_list.append({
                'emp_id': emp_id,
                'emp_name': data['emp_name'],
                'total_hours': f"{data['total_hours']:.2f}",
                'billable_hours': f"{data['billable_hours']:.2f}",
                'non_billable_hours': f"{data['non_billable_hours']:.2f}",
                'leave_hours': f"{data['leave_hours']:.2f}",
                'billable_cost': f"{data['billable_cost']:.2f}",
                'non_billable_cost': f"{data['non_billable_cost']:.2f}",
                'utilization_percent': f"{utilization:.2f}",
            })
        
        print('Before filtering the low hours: ', report_data_list)


        if week_filter == 'low_hours':

            report_data_list = [d for d in report_data_list if Decimal(d['total_hours']) < 140]

        print('After filtering the low hours: ', report_data_list)

        report_data = report_data_list
        table_headers = [
            {'title': 'Employee ID', 'data': 'emp_id'},
            {'title': 'Employee Name', 'data': 'emp_name'},
            {'title': 'Total Hours', 'data': 'total_hours'},
            {'title': 'Billable Hours', 'data': 'billable_hours'},
            {'title': 'Non-Billable Hours', 'data': 'non_billable_hours'},
            {'title': 'Leave Hours', 'data': 'leave_hours'},
            {'title': 'Billable Cost', 'data': 'billable_cost'},
            {'title': 'Non-Billable Cost', 'data': 'non_billable_cost'},
            {'title': 'Utilization %', 'data': 'utilization_percent'},
        ]
        filterable_columns = ['Employee Name']
        unsortable_columns = ['Employee Name']
        template_name = 'reports/reports_table_project_cost.html'

    elif report_type == 'timesheet_log_reports':
        # Default date range: current month
        today = date.today()
        default_start = today.replace(day=1)
        default_end = (default_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Get date range from request
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = date.fromisoformat(start_date_str) if start_date_str else default_start
        end_date = date.fromisoformat(end_date_str) if end_date_str else default_end

        # Base queryset: Only Approved
        qs = Timesheet.objects.filter(status='Approved', date__range=(start_date, end_date)).select_related('resource', 'project', 'task', 'reviewed_by')
        print("Queryset count:", qs.count())
        # Access control
        user = request.user
        resource = getattr(user, 'resource', None)
        print("Before filtering the user record based on the reporting: ", qs)
        if resource:
            if access_level is not None:
                if access_level <= 2:
                    qs = qs.filter(resource=resource)
                elif access_level == 3:
                    reporting_emp_ids = Resource.objects.filter(reporting_to=resource).values_list('id', flat=True)
                    qs = qs.filter(resource_id__in=reporting_emp_ids)
                    print("Reporting user log reports: ", qs)
                # access_level == 4 => all records, no filtering

        report_data_list = []
        for entry in qs:
            report_data_list.append({
                'date': entry.date.strftime('%Y-%m-%d'),
                'emp_id': entry.resource.emp_id,
                'emp_name': entry.resource.name,
                'project': entry.project.name,
                'task': entry.task.name if entry.task else '',
                'description': entry.task_description or '',
                'hours': f"{entry.hours:.2f}",
                'status': entry.status,
                'reviewed_by': entry.reviewed_by.name if entry.reviewed_by else '',
            })

        report_data = report_data_list
        table_headers = [
            {'title': 'Date', 'data': 'date'},
            {'title': 'Employee ID', 'data': 'emp_id'},
            {'title': 'Employee Name', 'data': 'emp_name'},
            {'title': 'Project', 'data': 'project'},
            {'title': 'Task', 'data': 'task'},
            {'title': 'Description', 'data': 'description'},
            {'title': 'Hours', 'data': 'hours'},
            {'title': 'Status', 'data': 'status'},
            {'title': 'Reviewed By', 'data': 'reviewed_by'},
        ]

        filterable_columns = ['Employee Name', 'Project', 'Status', 'Reviewed By']
        unsortable_columns = ['Employee Name', 'Project', 'Status', 'Reviewed By', 'Task', 'Description', 'Hours']
        template_name = 'reports/reports_table_project_cost.html'
    
            
    context = {
        'report_type': request.GET.get('report_type', 'timesheet_log_reports'),
        'template_name': template_name,

        'report_data': report_data,
        'table_headers': table_headers,
        'filterable_columns': filterable_columns,
        'unsortable_columns': unsortable_columns,
        'has_data': bool(report_data),
        'start_date': default_start.strftime('%Y-%m-%d') if isinstance(default_start, date) else '',
        'end_date': default_end.strftime('%Y-%m-%d') if isinstance(default_end, date) else '',
        'access_level': access_level,
    }
    print("Report Type: ", report_type)
    # return render(request, 'reports_table_project_cost.html', context)
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
