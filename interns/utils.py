from datetime import timedelta
from django.utils import timezone


def get_working_days_count(start_date, end_date):
    """
    Calculates total weekdays (Monday through Friday) between start_date and end_date inclusive.
    Excludes Saturday (weekday 5) and Sunday (weekday 6).
    """
    if not start_date or not end_date or start_date > end_date:
        return 0

    total_days = (end_date - start_date).days + 1
    working_days = 0

    for day_offset in range(total_days):
        current_day = start_date + timedelta(days=day_offset)
        # 0 = Monday, ..., 4 = Friday, 5 = Saturday, 6 = Sunday
        if current_day.weekday() < 5:
            working_days += 1

    return working_days


def calculate_internship_progress(internship, current_date=None):
    """
    Calculates working-day metrics and progress percentage for an internship.

    Returns dict with keys:
        - total_working_days
        - completed_working_days
        - remaining_working_days
        - progress_percentage (clamped 0 to 100)
    """
    if current_date is None:
        current_date = timezone.now().date()

    start_date = internship.start_date
    expected_end = internship.expected_end_date

    total_working_days = get_working_days_count(start_date, expected_end)

    if total_working_days == 0:
        return {
            'total_working_days': 0,
            'completed_working_days': 0,
            'remaining_working_days': 0,
            'progress_percentage': 0,
        }

    status = getattr(internship, 'status', 'ACTIVE')

    if status == 'COMPLETED':
        return {
            'total_working_days': total_working_days,
            'completed_working_days': total_working_days,
            'remaining_working_days': 0,
            'progress_percentage': 100,
        }

    if status == 'CANCELLED':
        if current_date < start_date:
            completed = 0
        else:
            as_of_date = min(current_date, expected_end)
            completed = min(get_working_days_count(start_date, as_of_date), total_working_days)

        pct = round((completed / total_working_days) * 100)
        return {
            'total_working_days': total_working_days,
            'completed_working_days': completed,
            'remaining_working_days': 0,
            'progress_percentage': min(100, max(0, pct)),
        }

    # PENDING or ACTIVE status
    if current_date < start_date:
        completed = 0
        remaining = total_working_days
        progress = 0
    elif current_date >= expected_end:
        completed = total_working_days
        remaining = 0
        progress = 100
    else:
        completed = get_working_days_count(start_date, current_date)
        remaining = get_working_days_count(current_date + timedelta(days=1), expected_end)
        raw_pct = (completed / total_working_days) * 100
        progress = int(round(raw_pct))
        progress = min(100, max(0, progress))

    return {
        'total_working_days': total_working_days,
        'completed_working_days': completed,
        'remaining_working_days': remaining,
        'progress_percentage': progress,
    }
