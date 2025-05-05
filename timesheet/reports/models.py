from django.db import models

class ProjectReportMV(models.Model):
    project_code = models.CharField(max_length=50, primary_key=True)  # Set project_code as the primary key
    client_name = models.CharField(max_length=255)  # Client name column
    project_name = models.CharField(max_length=255)  # Project name column
    project_status = models.CharField(max_length=50)  # Project status column
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)  # Total budget
    allotted_hours = models.DecimalField(max_digits=10, decimal_places=2)  # Allotted hours
    worked_hours = models.DecimalField(max_digits=10, decimal_places=2)  # Worked hours
    remaining_hours = models.DecimalField(max_digits=10, decimal_places=2)  # Remaining hours
    cost_spent = models.DecimalField(max_digits=10, decimal_places=2)  # Cost spent
    remaining_budget = models.DecimalField(max_digits=10, decimal_places=2)  # Remaining budget
    percent_budget_used = models.DecimalField(max_digits=5, decimal_places=2)  # Percent budget used
    percent_time_used = models.DecimalField(max_digits=5, decimal_places=2)  # Percent time used
    num_resources_assigned = models.IntegerField()  # Number of resources assigned
    project_lead_name = models.CharField(max_length=255)  # Project lead name
    delivery_head_name = models.CharField(max_length=255)  # Delivery head name

    class Meta:
        managed = False
        db_table = "project_report1_mv"

class ProjectTaskTracking(models.Model):
    project_id = models.IntegerField(primary_key=True)
    project_name = models.CharField(max_length=50,)
    task_name = models.CharField(max_length=50)
    task_status = models.CharField(max_length=50)
    worked_hours = models.FloatField()
    allotted_hours = models.FloatField()
    remaining_hours = models.FloatField()
    cost_spent = models.FloatField()

    class Meta:
        managed = False
        db_table = 'project_task_trakcing_mv'


class EmployeeUtilizationMV(models.Model):
    emp_id = models.CharField(max_length=50, primary_key=True)
    emp_name = models.CharField(max_length=255)
    date = models.DateField()
    project_id = models.IntegerField()
    project_name = models.CharField(max_length=255)
    commercial = models.CharField(max_length=50)
    hours_worked = models.FloatField()
    cost_spent = models.FloatField()
    status = models.CharField(max_length=50)
    is_leave_day = models.BooleanField()
    is_working_day = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'employee_utilization_mv'
