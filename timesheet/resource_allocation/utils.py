from datetime import timedelta
from django.utils import timezone
from core.models import Holiday  # adjust import as needed

def get_weekly_capacity(week_start_date=None):
    if week_start_date is None:
        today = timezone.now().date()
        week_start_date = today - timedelta(days=today.weekday())  # Monday of the current week

    week_end_date = week_start_date + timedelta(days=6)  # Sunday of the same week

    # Weekdays (Mon-Fri) excluding holidays
    working_days = [
        week_start_date + timedelta(days=i)
        for i in range(7)
        if (week_start_date + timedelta(days=i)).weekday() < 5  # Mon-Fri
    ]

    # Get holidays within the week range
    holidays = set(Holiday.objects.filter(date__range=(week_start_date, week_end_date)).values_list('date', flat=True))

    # Available working days are weekdays not in the holidays
    available_days = [day for day in working_days if day not in holidays]

    # Assuming 8 working hours per day
    return len(available_days) * 8
