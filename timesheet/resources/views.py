from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from core.models import Resource
from .forms import ResourceForm
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

ROLE_HIERARCHY = {
    'Software Engineer': 'Project Lead',
    'Software Engineer Trainee': 'Project Lead',
    'Project Lead': 'Delivery Lead',
    'Delivery Lead': 'Department Head',
}
ALLOWED_LOGIN_ROLES = ['Project Lead', 'Delivery Lead', 'Department Head']

@login_required
def resources_view(request):
    resources = Resource.objects.all()
    return render(request, 'resources/resources.html', {
        'resources': resources,
    })

@login_required
def save_resource(request):
    resource_id = request.POST.get('resource_id')
    instance = get_object_or_404(Resource, id=resource_id) if resource_id else None

    form = ResourceForm(request.POST, instance=instance)

    if form.is_valid():
        # Extract data BEFORE saving the resource
        emp_id = form.cleaned_data['emp_id']

        if not instance and Resource.objects.filter(emp_id=emp_id).exists():
            form.add_error('emp_id', 'A resource with this Employee ID already exists.')
            html = render_to_string('resources/partials/resource_form_inner.html', {'form': form, 'resource': instance}, request=request)
            return HttpResponse(html, status=400)


        email = form.cleaned_data['email']
        name = form.cleaned_data['name']
        role = form.cleaned_data['role']

        # Create or update Django User
        user, created = User.objects.get_or_create(
            username=emp_id,
            defaults={
                'email': email,
                'first_name': name,
                'password': make_password('admin@123'),  # Always hash passwords
                'is_active': role in ALLOWED_LOGIN_ROLES
            }
        )
        if not created:
            user.email = email
            user.first_name = name
            user.save()

        # Now assign the user to the resource
        resource = form.save(commit=False)
        resource.user = user  # Assuming you have a user = models.OneToOneField(...) in Resource
        resource.save()
        form.save_m2m()

        resources = Resource.objects.all()
        html = render_to_string('resources/partials/resource_table.html', {'resources': resources})
        response = HttpResponse(html)
        response['HX-Trigger'] = 'resourceSaved'
        return response
    else:
        html = render_to_string('resources/partials/resource_form_inner.html', {'form': form, 'resource': instance}, request=request)
        return HttpResponse(html, status=400)

@login_required
def load_new_resource_form(request):
    form = ResourceForm()
    html = render_to_string('resources/partials/resource_form_inner.html', {'form': form, 'resource': None}, request=request)
    return HttpResponse(html)

@login_required
def load_resource_form(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    form = ResourceForm(instance=resource)

    role = resource.role
    reporting_to_role = ROLE_HIERARCHY.get(role)
    reporting_to_options = Resource.objects.filter(role__iexact=reporting_to_role)

    html = render_to_string('resources/partials/resource_form_inner.html', {'form': form, 'resource': resource,'reporting_to_options': reporting_to_options}, request=request)
    return HttpResponse(html)

def load_reporting_to_options(request):
    role = request.GET.get('role')
    selected_id = request.GET.get('selected_id')
    reporting_to_role = ROLE_HIERARCHY.get(role)

    if reporting_to_role:
        reporting_to_options = Resource.objects.filter(role__iexact=reporting_to_role)
    else:
        reporting_to_options = Resource.objects.none()

    html = render_to_string('resources/reporting_to_dropdown.html', {
        'reporting_to_options': reporting_to_options,
        'selected_id': selected_id,
    })
    return HttpResponse(html)