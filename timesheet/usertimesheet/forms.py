from django import forms
from core.models import Timesheet, Task, SubTask

##working code without approval functionality

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['project', 'task', 'subtask', 'task_description', 'hours']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically populate subtasks based on selected task (if exists)
        if 'task' in self.data:
            try:
                task_id = int(self.data.get('task'))
                self.fields['subtask'].queryset = SubTask.objects.filter(task_id=task_id)
            except (ValueError, TypeError):
                self.fields['subtask'].queryset = SubTask.objects.none()
        elif self.instance.pk and self.instance.task:
            self.fields['subtask'].queryset = self.instance.task.subtasks.all()
        else:
            self.fields['subtask'].queryset = SubTask.objects.none()

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['status', 'review_comment']
        widgets = {
            'review_comment': forms.Textarea(attrs={'rows': 3}),
        }
        
# class SelfTimesheetEditForm(forms.ModelForm):
#     class Meta:
#         model = Timesheet
#         fields = ['project', 'task', 'subtask', 'task_description', 'hours']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if 'task' in self.data:
#             try:
#                 task_id = int(self.data.get('task'))
#                 self.fields['subtask'].queryset = SubTask.objects.filter(task_id=task_id)
#             except (ValueError, TypeError):
#                 self.fields['subtask'].queryset = SubTask.objects.none()
#         elif self.instance.pk and self.instance.task:
#             self.fields['subtask'].queryset = self.instance.task.subtasks.all()
#         else:
#             self.fields['subtask'].queryset = SubTask.objects.none()


# class TimesheetApprovalForm(forms.ModelForm):
#     class Meta:
#         model = Timesheet
#         fields = ['status', 'review_comment']
#         widgets = {
#             'review_comment': forms.Textarea(attrs={'rows': 2}),
#         }

