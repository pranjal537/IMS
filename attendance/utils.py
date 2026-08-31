from django.utils import timezone
from interns.utils import get_working_days_count
from .models import Attendance, AttendanceStatus


def calculate_intern_attendance_stats(intern_profile, as_of_date=None):
    """
    Calculates attendance metrics for an intern:
        - total_working_days
        - present_days
        - leave_days
        - absent_days
        - attendance_percentage (clamped 0 to 100)
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()

    internship = getattr(intern_profile, 'internship', None)
    if not internship:
        return {
            'total_working_days': 0,
            'present_days': 0,
            'leave_days': 0,
            'absent_days': 0,
            'attendance_percentage': 0.0,
        }

    start_date = internship.start_date
    expected_end = internship.expected_end_date

    # If internship has not started yet as of as_of_date
    if as_of_date < start_date:
        return {
            'total_working_days': 0,
            'present_days': 0,
            'leave_days': 0,
            'absent_days': 0,
            'attendance_percentage': 0.0,
        }

    # Effective end for total expected working days up to current date
    end_boundary = min(as_of_date, expected_end)
    total_working_days = get_working_days_count(start_date, end_boundary)

    # Attendance counts
    qs = Attendance.objects.filter(intern=intern_profile)
    present_days = qs.filter(status=AttendanceStatus.PRESENT).count()
    leave_days = qs.filter(status=AttendanceStatus.LEAVE).count()
    absent_days = qs.filter(status=AttendanceStatus.ABSENT).count()

    if total_working_days > 0:
        raw_pct = (present_days / total_working_days) * 100.0
        attendance_percentage = min(100.0, max(0.0, round(raw_pct, 1)))
    else:
        attendance_percentage = 0.0

    return {
        'total_working_days': total_working_days,
        'present_days': present_days,
        'leave_days': leave_days,
        'absent_days': absent_days,
        'attendance_percentage': attendance_percentage,
    }
