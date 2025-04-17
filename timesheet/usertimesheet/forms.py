from django import forms
from core.models import Resource

class TimesheetForm(forms.Form):
    employee_id = forms.ModelChoiceField(
        queryset=Resource.objects.none(),  # will be filtered in __init__
        label='Employee',
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Assuming Resource.reporting_to is a ForeignKey to the logged-in manager
            self.fields['employee_id'].queryset = Resource.objects.filter(reporting_to__user=user)
