from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_POST
from datetime import datetime

from accounts.decorators import supervisor_required, intern_required
from interns.models import Department, InternProfile, InternshipStatus
from .models import Attendance, AttendanceStatus
from .forms import SupervisorAttendanceForm
from .utils import calculate_intern_attendance_stats


# ─── Intern Attendance Views ──────────────────────────────────────────────────

@intern_required
def intern_attendance_today_view(request):
    """
    Intern Today's Attendance page.
    Displays check-in status, Check In button, and Check Out button for current date.
    """
    intern_profile = getattr(request.user, 'intern_profile', None)
    if not intern_profile:
        messages.error(request, "Intern profile not found. Please contact administration.")
        return render(request, 'attendance/intern_attendance_today.html', {'today_record': None})

    today = timezone.now().date()
    today_record = Attendance.objects.filter(intern=intern_profile, date=today).first()
    stats = calculate_intern_attendance_stats(intern_profile)

    context = {
        'page_title': "Today's Attendance",
        'today': today,
        'today_record': today_record,
        'stats': stats,
        'is_weekend': today.weekday() >= 5, # 5 = Sat, 6 = Sun
    }
    return render(request, 'attendance/intern_attendance_today.html', context)


@intern_required
@require_POST
def intern_mark_present_view(request):
    """Action: Mark Present / Check In for today."""
    intern_profile = getattr(request.user, 'intern_profile', None)
    if not intern_profile:
        messages.error(request, "Intern profile not found.")
        return redirect('attendance:intern_today')

    today = timezone.now().date()
    now_time = timezone.now().time()

    # Weekend check
    if today.weekday() >= 5:
        messages.error(request, "Attendance marking is not allowed on weekends (Saturday/Sunday).")
        return redirect('attendance:intern_today')

    # Internship placement check
    internship = getattr(intern_profile, 'internship', None)
    if not internship:
        messages.error(request, "You do not have an active internship placement.")
        return redirect('attendance:intern_today')

    if today < internship.start_date:
        messages.error(request, "Your internship has not started yet.")
        return redirect('attendance:intern_today')

    end_boundary = internship.actual_end_date or internship.expected_end_date
    if today > end_boundary:
        messages.error(request, "Your internship has already ended.")
        return redirect('attendance:intern_today')

    # Check for existing record for today
    existing = Attendance.objects.filter(intern=intern_profile, date=today).first()
    if existing:
        messages.warning(request, f"Attendance already recorded for today (Status: {existing.get_status_display()}).")
        return redirect('attendance:intern_today')

    # Create new attendance record
    Attendance.objects.create(
        intern=intern_profile,
        date=today,
        check_in=now_time,
        status=AttendanceStatus.PRESENT
    )
    messages.success(request, f"Check-in recorded successfully at {now_time.strftime('%I:%M %p')}.")
    return redirect('attendance:intern_today')


@intern_required
@require_POST
def intern_checkout_view(request):
    """Action: Check Out for today."""
    intern_profile = getattr(request.user, 'intern_profile', None)
    if not intern_profile:
        messages.error(request, "Intern profile not found.")
        return redirect('attendance:intern_today')

    today = timezone.now().date()
    now_time = timezone.now().time()

    today_record = Attendance.objects.filter(intern=intern_profile, date=today).first()
    if not today_record:
        messages.error(request, "No check-in record found for today. Please check in first.")
        return redirect('attendance:intern_today')

    if today_record.check_out:
        messages.warning(request, f"You have already checked out today at {today_record.check_out.strftime('%I:%M %p')}.")
        return redirect('attendance:intern_today')

    today_record.check_out = now_time
    today_record.save()
    messages.success(request, f"Check-out recorded successfully at {now_time.strftime('%I:%M %p')}.")
    return redirect('attendance:intern_today')


@intern_required
def intern_attendance_history_view(request):
    """
    Intern Attendance History page.
    List of past attendance records for the logged-in intern with status and month filters.
    """
    intern_profile = getattr(request.user, 'intern_profile', None)
    if not intern_profile:
        messages.error(request, "Intern profile not found.")
        return render(request, 'attendance/intern_attendance_history.html', {'records': []})

    queryset = Attendance.objects.filter(intern=intern_profile).order_by('-date')

    # Status filter
    selected_status = request.GET.get('status', '').strip()
    if selected_status:
        queryset = queryset.filter(status=selected_status)

    # Month filter (format YYYY-MM)
    selected_month = request.GET.get('month', '').strip()
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            queryset = queryset.filter(date__year=year, date__month=month)
        except ValueError:
            pass

    stats = calculate_intern_attendance_stats(intern_profile)

    context = {
        'page_title': 'Attendance History',
        'records': queryset,
        'stats': stats,
        'statuses': AttendanceStatus.choices,
        'selected_status': selected_status,
        'selected_month': selected_month,
    }
    return render(request, 'attendance/intern_attendance_history.html', context)


# ─── Supervisor Attendance Views ──────────────────────────────────────────────

@supervisor_required
def supervisor_attendance_list_view(request):
    """
    Supervisor Attendance Monitoring.
    Lists attendance ONLY for interns assigned under the logged-in supervisor.
    """
    supervisor_profile = getattr(request.user, 'supervisor_profile', None)
    if not supervisor_profile:
        messages.warning(request, "Supervisor profile not found.")
        return render(request, 'attendance/supervisor_attendance_list.html', {'records': []})

    # Restrict server-side to assigned interns
    queryset = Attendance.objects.filter(
        intern__internship__supervisor=supervisor_profile
    ).select_related('intern', 'intern__user', 'intern__internship', 'intern__internship__department').order_by('-date', 'intern__user__first_name')

    # Filters
    search_query = request.GET.get('q', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(intern__user__first_name__icontains=search_query) |
            Q(intern__user__last_name__icontains=search_query) |
            Q(intern__intern_id__icontains=search_query)
        )

    selected_status = request.GET.get('status', '').strip()
    if selected_status:
        queryset = queryset.filter(status=selected_status)

    selected_date = request.GET.get('date', '').strip()
    if selected_date:
        queryset = queryset.filter(date=selected_date)

    # Get assigned interns list for filter dropdown
    assigned_interns = InternProfile.objects.filter(internship__supervisor=supervisor_profile)

    selected_intern = request.GET.get('intern', '').strip()
    if selected_intern:
        queryset = queryset.filter(intern_id=selected_intern)

    context = {
        'page_title': 'Intern Attendance Monitoring',
        'records': queryset,
        'assigned_interns': assigned_interns,
        'statuses': AttendanceStatus.choices,
        'search_query': search_query,
        'selected_status': selected_status,
        'selected_date': selected_date,
        'selected_intern': selected_intern,
    }
    return render(request, 'attendance/supervisor_attendance_list.html', context)


@supervisor_required
def supervisor_attendance_create_view(request):
    """Supervisor creates or logs attendance/leave record for an assigned intern."""
    supervisor_profile = getattr(request.user, 'supervisor_profile', None)
    if not supervisor_profile:
        messages.error(request, "Supervisor profile not found.")
        return redirect('attendance:supervisor_list')

    if request.method == 'POST':
        form = SupervisorAttendanceForm(request.POST, supervisor_profile=supervisor_profile)
        if form.is_valid():
            attendance = form.save(commit=False)
            # Security verification: ensure selected intern is assigned to supervisor
            if attendance.intern.internship.supervisor != supervisor_profile:
                messages.error(request, "You can only manage attendance for your assigned interns.")
                return redirect('attendance:supervisor_list')
            attendance.save()
            messages.success(request, f"Attendance record saved for {attendance.intern.user.get_full_name()} ({attendance.date}).")
            return redirect('attendance:supervisor_list')
    else:
        initial_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        form = SupervisorAttendanceForm(supervisor_profile=supervisor_profile, initial={'date': initial_date})

    return render(request, 'attendance/supervisor_attendance_form.html', {
        'form': form,
        'page_title': 'Add Attendance / Leave Record',
        'title': 'Add Attendance / Leave Record',
    })


@supervisor_required
def supervisor_attendance_edit_view(request, pk):
    """Supervisor edits an existing attendance record for an assigned intern."""
    supervisor_profile = getattr(request.user, 'supervisor_profile', None)
    if not supervisor_profile:
        messages.error(request, "Supervisor profile not found.")
        return redirect('attendance:supervisor_list')

    attendance = get_object_or_404(Attendance, pk=pk)

    # Security check: Ensure attendance belongs to an intern assigned to this supervisor
    if attendance.intern.internship.supervisor != supervisor_profile:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = SupervisorAttendanceForm(request.POST, instance=attendance, supervisor_profile=supervisor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Attendance record for {attendance.intern.user.get_full_name()} updated successfully.")
            return redirect('attendance:supervisor_list')
    else:
        form = SupervisorAttendanceForm(instance=attendance, supervisor_profile=supervisor_profile)

    return render(request, 'attendance/supervisor_attendance_form.html', {
        'form': form,
        'attendance': attendance,
        'page_title': 'Edit Attendance Record',
        'title': f'Edit Attendance: {attendance.intern.user.get_full_name()} ({attendance.date})',
    })
