# from django import forms
# from django.forms import modelformset_factory
# from core.models import ResourceAllocation

# class ResourceAllocationForm(forms.ModelForm):
#     class Meta:
#         model = ResourceAllocation
#         fields = ['resource', 'assigned_hours']
#         widgets = {
#             'resource': forms.Select(attrs={'class': 'form-control'}),
#             'assigned_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
#         }

# ResourceAllocationFormSet = modelformset_factory(
#     ResourceAllocation,
#     form=ResourceAllocationForm,
#     extra=3,  # Show 3 empty rows for new entries
#     can_delete=False
# )
