from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date

# Role hierarchy for approvals
ROLE_HIERARCHY = {
    'Software Engineer': 'Project Lead',
    'Software Engineer Trainee': 'Project Lead',
    'Project Lead': 'Delivery Lead',
    'Delivery Lead': 'Department Head',
}

# Client Table
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    location = models.CharField(max_length=100)
    client_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.client_code:
            last_code = Client.objects.all().order_by('-id').first()
            next_num = (int(last_code.client_code[1:]) + 1) if last_code else 1
            self.client_code = f'C{next_num:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Department Table
class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.ForeignKey('Resource', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Role name
    access_level = models.IntegerField()  # Integer value for role access level (if required)

    def __str__(self):
        return self.name

# Resource Table (Employees)
class Resource(models.Model):
    ROLE_CHOICES = [
        ('Project Lead', 'Project Lead'),
        ('Department Head', 'Department Head'),
        ('Delivery Lead', 'Delivery Lead'),
        ('Lead UI/UX Developer', 'Lead UI/UX Developer'),
        ('Software Engineer Trainee', 'Software Engineer Trainee'),
        ('Software Engineer', 'Software Engineer'),
        ('Senior Software Engineer', 'Senior Software Engineer'),
        ('Intern - Software Engineer', 'Intern - Software Engineer'),
        ('Senior Automation Engineer', 'Senior Automation Engineer'),
        ('Data Analyst', 'Data Analyst'),
        ('Automation Engineer', 'Automation Engineer'),
        ('System Analyst', 'System Analyst'),
        ('Junior Automation Engineer', 'Junior Automation Engineer'),
        ('ESG Data Analyst Intern', 'ESG Data Analyst Intern'),

    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)  
    assigned_projects = models.ManyToManyField('Project', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    
    # Optional - for hierarchy (can be removed later if not used)
    reporting_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)


    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        help_text="Rate per hour for billing purposes"
    )
    def __str__(self):
        return f"{self.name} ({self.emp_id})"

    def save(self, *args, **kwargs):
        if not self.user:
            username = self.emp_id
            password = 'admin123'
            user = User.objects.create_user(username=username, password=password, email=self.email)
            user.first_name = self.name
            self.user = user

        if self.user:
            self.user.is_staff = self.role in ['Department Head', 'Project Lead', 'Delivery Lead']
            self.user.is_active = True
            self.user.first_name = self.name
            self.user.email = self.email
            self.user.save()

        super().save(*args, **kwargs)



# Project Table
class Project(models.Model):
    BILLABLE_TYPE_CHOICES = [
        ('Billable', 'Billable'),
        ('Non-Billable', 'Non-Billable'),
    ]
    PROJECT_TYPE_CHOICES = [
        ('Continuous', 'Continuous'),
        ('Onetime', 'Onetime'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inprogress', 'Inprogress'),
        ('Completed', 'Completed'),
        ('Discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    commercial = models.CharField(max_length=20, choices=BILLABLE_TYPE_CHOICES)
    type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    
    # New field for project-specific approval
    project_lead = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_projects',
        limit_choices_to={'role__access_level': 3}
    )

    delivery_head = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__access_level': 4}
    )

    budget = models.DecimalField(max_digits=12, decimal_places=2)
    project_code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.project_code:
            year = date.today().year
            client_code = self.client.client_code
            base = f'DT-{year}-{client_code}'

            last_project = Project.objects.filter(project_code__startswith=base).order_by('-id').first()
            last_num = int(last_project.project_code.split('-')[-1]) if last_project and last_project.project_code else 0
            self.project_code = f'{base}-{last_num + 1}'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Task Models
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Project Task Assignment
class ProjectTaskAssignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assigned_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, null=True, blank=True)
    allotted_hours = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('project', 'task', 'subtask')

    def __str__(self):
        return f"{self.project.name} - {self.task.name} - {self.subtask.name if self.subtask else ''}"

class Timesheet(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    subtask = models.ForeignKey(SubTask, on_delete=models.SET_NULL, null=True, blank=True)
    task_description = models.TextField(blank=True, null=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    #newly added fidls
    reviewed_by = models.ForeignKey(Resource, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_entries')
    review_comment = models.TextField(blank=True, null=True)
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.resource.name} - {self.project.name} ({self.date})"




# # Timesheet Table
# class Timesheet(models.Model):
#     resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     task_description = models.TextField()
#     hours = models.DecimalField(max_digits=5, decimal_places=2)
#     date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.resource.name} - {self.project.name} ({self.date})"
