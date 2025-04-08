from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Client Table
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    location = models.CharField(max_length=100)

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

    def __str__(self):
        return self.name

# Resource Table (Employees)
class Resource(models.Model):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Department Head', 'Department Head'),
        ('Developer', 'Developer'),
        ('Tester', 'Tester'),
        ('Designer', 'Designer'),
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

    def save(self, *args, **kwargs):
        # Create linked User if not already created
        if not self.user:
            username = self.emp_id
            password = 'admin123'
            user = User.objects.create_user(username=username, password=password, email=self.email)
            user.first_name = self.name
            user.save()
            self.user = user
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
