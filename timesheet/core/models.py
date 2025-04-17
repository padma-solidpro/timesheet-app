from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

ROLE_HIERARCHY = {
    'Software Engineer': 'Project Lead',
    'Software Engineer Trainee': 'Project Lead',
    'Project Lead': 'Delivery Lead',
    'Delivery Lead': 'Department Head',
    'Software Engineer Trainee': 'Project Lead'
}

class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.ForeignKey('Resource', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')


    def __str__(self):
        return self.name

# Client Table
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    location = models.CharField(max_length=100)
    client_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.client_code:
            last_code = client.objects.all().order_by('-id').first()
            next_num = (int(last_code.client_code[1:]) + 1) if last_code else 1
            self.client_code = f'C{next_num:03d}'
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

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
        ('Completed', 'Completed'),
        ('Discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    commercial = models.CharField(max_length=20, choices=BILLABLE_TYPE_CHOICES)
    type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    delivery_head = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    project_code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.project_code:
            from datetime import date
            year = date.today().year
            client_code = self.client.client_code  # assuming FK to Client
            base = f'DT-{year}-{client_code}'
            
            last_project = Project.objects.filter(project_code__startswith=base).order_by('-id').first()
            if last_project and last_project.project_code:
                last_num = int(last_project.project_code.split('-')[-1])
            else:
                last_num = 0
            self.project_code = f'{base}-{last_num + 1}'
    
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Resource Table (Employees)
class Resource(models.Model):
    ROLE_CHOICES = [
        ('Project Lead', 'Project Lead'),
        ('Department Head', 'Department Head'),
        ('Delivery Lead', 'Delivery Lead'),
        ('Software Engineer', 'Software Engineer'),
        ('Software Engineer Trainee', 'Software Engineer Trainee'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    assigned_projects = models.ManyToManyField(Project, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    reporting_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reportees'
    )
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        help_text="Rate per hour for billing purposes"
    )

    def save(self, *args, **kwargs):
        # Create linked User if not already created
        if not self.user:
            username = self.emp_id
            password = 'admin123'
            user = User.objects.create_user(username=username, password=password, email=self.email)
            user.first_name = self.name

        if self.user:
            if self.role in ['Department Head', 'Project Lead', 'Delivery Head']:
                self.user.is_staff = True
                self.user.is_active = True
            else:
                self.user.is_staff = False
                self.user.is_active = False
            self.user.first_name = self.name
            self.user.email = self.email
            self.user.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.emp_id})"

# Timesheet Table
class Timesheet(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_description = models.TextField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} - {self.project.name} ({self.date})"

