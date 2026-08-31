"""
Logbook views for Damak Municipality IMS.
Phase 5: Daily Logbook / Activity Tracking.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.views.decorators.http import require_POST

from accounts.decorators import intern_required, supervisor_required
from interns.models import InternProfile
from attendance.models import Attendance, AttendanceStatus
from .models import DailyLog, DailyLogStatus
from .forms import DailyLogForm, SupervisorFeedbackForm


# ═══════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════

def calculate_intern_log_stats(intern_profile):
    """
    Returns logbook statistics for an intern.
    Dict keys: total, approved, pending, rejected, total_hours
    """
    qs = DailyLog.objects.filter(intern=intern_profile)
    total = qs.count()
    approved = qs.filter(status=DailyLogStatus.APPROVED).count()
    pending = qs.filter(status=DailyLogStatus.PENDING).count()
    rejected = qs.filter(status=DailyLogStatus.REJECTED).count()
    total_hours = qs.aggregate(h=Sum('hours_worked'))['h'] or 0
    return {
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'total_hours': total_hours,
    }


def _get_intern_profile_or_redirect(request, redirect_url='intern_logbook'):
    """Get intern_profile for the logged-in intern user."""
    return getattr(request.user, 'intern_profile', None)


def _get_supervisor_profile_or_redirect(request):
    """Get supervisor_profile for the logged-in supervisor user."""
    return getattr(request.user, 'supervisor_profile', None)


# ═══════════════════════════════════════════════════════════════
#  Intern Views
# ═══════════════════════════════════════════════════════════════

@intern_required
def intern_logbook_list_view(request):
    """
    /intern/logbook/
    Shows the intern's own logbook history with statistics and filters.
    """
    intern_profile = _get_intern_profile_or_redirect(request)
    if not intern_profile:
        messages.error(request, "Intern profile not found. Please contact administration.")
        return render(request, 'logbook/intern_logbook_list.html', {'logs': [], 'stats': {}})

    queryset = DailyLog.objects.filter(intern=intern_profile).order_by('-date')

    # Status filter
    selected_status = request.GET.get('status', '').strip()
    if selected_status:
        queryset = queryset.filter(status=selected_status)

    # Month filter (YYYY-MM)
    selected_month = request.GET.get('month', '').strip()
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            queryset = queryset.filter(date__year=year, date__month=month)
        except (ValueError, AttributeError):
            pass

    stats = calculate_intern_log_stats(intern_profile)

    context = {
        'page_title': 'My Daily Logbook',
        'logs': queryset,
        'stats': stats,
        'statuses': DailyLogStatus.choices,
        'selected_status': selected_status,
        'selected_month': selected_month,
    }
    return render(request, 'logbook/intern_logbook_list.html', context)


@intern_required
def intern_log_create_view(request):
    """
    /intern/logbook/create/
    Create a new daily log entry. Attendance warning shown if no PRESENT record.
    """
    intern_profile = _get_intern_profile_or_redirect(request)
    if not intern_profile:
        messages.error(request, "Intern profile not found.")
        return redirect('intern_logbook')

    today = timezone.now().date()
    attendance_warning = None

    if request.method == 'POST':
        form = DailyLogForm(request.POST, intern_profile=intern_profile)
        if form.is_valid():
            log_date = form.cleaned_data['date']

            # Check for duplicate (friendly message before model-level error)
            if DailyLog.objects.filter(intern=intern_profile, date=log_date).exists():
                existing_log = DailyLog.objects.get(intern=intern_profile, date=log_date)
                messages.warning(
                    request,
                    f"You have already submitted a daily log for {log_date.strftime('%B %d, %Y')}. "
                    f"You can view or edit it below."
                )
                return redirect('intern_log_detail', pk=existing_log.pk)

            log = form.save(commit=False)
            log.intern = intern_profile
            log.status = DailyLogStatus.PENDING
            log.save()
            messages.success(
                request,
                f"Daily log for {log.date.strftime('%B %d, %Y')} submitted successfully. "
                f"Status: Pending review."
            )
            return redirect('intern_logbook')
        # On form error, check attendance for the submitted date
        submitted_date = request.POST.get('date')
        if submitted_date:
            try:
                from datetime import date as date_type
                import datetime
                log_date = datetime.date.fromisoformat(submitted_date)
                has_attendance = Attendance.objects.filter(
                    intern=intern_profile, date=log_date, status=AttendanceStatus.PRESENT
                ).exists()
                if not has_attendance:
                    attendance_warning = log_date
            except (ValueError, TypeError):
                pass
    else:
        form = DailyLogForm(intern_profile=intern_profile, initial={'date': today.strftime('%Y-%m-%d')})
        # Show attendance warning for today if pre-populating with today
        has_today_attendance = Attendance.objects.filter(
            intern=intern_profile, date=today, status=AttendanceStatus.PRESENT
        ).exists()
        if not has_today_attendance and today.weekday() < 5:
            attendance_warning = today

    context = {
        'page_title': 'Add Daily Log',
        'form': form,
        'attendance_warning': attendance_warning,
        'is_edit': False,
    }
    return render(request, 'logbook/intern_log_form.html', context)


@intern_required
def intern_log_detail_view(request, pk):
    """
    /intern/logbook/<id>/
    Read-only detail view for the intern's own log. Shows supervisor feedback.
    """
    intern_profile = _get_intern_profile_or_redirect(request)
    if not intern_profile:
        messages.error(request, "Intern profile not found.")
        return redirect('intern_logbook')

    # Intern can only access their own log
    log = get_object_or_404(DailyLog, pk=pk, intern=intern_profile)

    context = {
        'page_title': f'Daily Log — {log.date.strftime("%B %d, %Y")}',
        'log': log,
    }
    return render(request, 'logbook/intern_log_detail.html', context)


@intern_required
def intern_log_edit_view(request, pk):
    """
    /intern/logbook/<id>/edit/
    Edit own PENDING or REJECTED log.
    Saving a REJECTED log resubmits it (sets status back to PENDING).
    APPROVED logs cannot be edited.
    """
    intern_profile = _get_intern_profile_or_redirect(request)
    if not intern_profile:
        messages.error(request, "Intern profile not found.")
        return redirect('intern_logbook')

    # Security: intern can only edit their own log
    log = get_object_or_404(DailyLog, pk=pk, intern=intern_profile)

    if log.is_approved:
        messages.warning(
            request,
            "This log has been approved and can no longer be edited."
        )
        return redirect('intern_log_detail', pk=pk)

    attendance_warning = None

    if request.method == 'POST':
        form = DailyLogForm(request.POST, instance=log, intern_profile=intern_profile)
        if form.is_valid():
            was_rejected = log.is_rejected
            updated_log = form.save(commit=False)
            # Resubmission: REJECTED → PENDING
            updated_log.status = DailyLogStatus.PENDING
            updated_log.save()
            if was_rejected:
                messages.success(
                    request,
                    "Log updated and resubmitted for supervisor review. Status: Pending."
                )
            else:
                messages.success(request, "Daily log updated successfully.")
            return redirect('intern_log_detail', pk=pk)
    else:
        form = DailyLogForm(instance=log, intern_profile=intern_profile)
        # Attendance warning for the current log date
        has_attendance = Attendance.objects.filter(
            intern=intern_profile, date=log.date, status=AttendanceStatus.PRESENT
        ).exists()
        if not has_attendance:
            attendance_warning = log.date

    context = {
        'page_title': f'Edit Daily Log — {log.date.strftime("%B %d, %Y")}',
        'form': form,
        'log': log,
        'attendance_warning': attendance_warning,
        'is_edit': True,
    }
    return render(request, 'logbook/intern_log_form.html', context)


# ═══════════════════════════════════════════════════════════════
#  Supervisor Views
# ═══════════════════════════════════════════════════════════════

@supervisor_required
def supervisor_logbook_list_view(request):
    """
    /supervisor/logbook/
    Lists daily logs belonging ONLY to interns assigned to this supervisor.
    Supports search (intern name, ID, title) and filters (intern, status, date).
    """
    supervisor_profile = _get_supervisor_profile_or_redirect(request)
    if not supervisor_profile:
        messages.warning(request, "Supervisor profile not found.")
        return render(request, 'logbook/supervisor_logbook_list.html', {'logs': []})

    queryset = DailyLog.objects.filter(
        intern__internship__supervisor=supervisor_profile
    ).select_related(
        'intern', 'intern__user', 'intern__internship', 'intern__internship__department'
    ).order_by('-date', 'intern__user__first_name')

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(intern__user__first_name__icontains=search_query) |
            Q(intern__user__last_name__icontains=search_query) |
            Q(intern__intern_id__icontains=search_query) |
            Q(title__icontains=search_query)
        )

    # Status filter
    selected_status = request.GET.get('status', '').strip()
    if selected_status:
        queryset = queryset.filter(status=selected_status)

    # Date filter
    selected_date = request.GET.get('date', '').strip()
    if selected_date:
        queryset = queryset.filter(date=selected_date)

    # Intern filter
    assigned_interns = InternProfile.objects.filter(
        internship__supervisor=supervisor_profile
    ).select_related('user')
    selected_intern = request.GET.get('intern', '').strip()
    if selected_intern:
        queryset = queryset.filter(intern_id=selected_intern)

    # Pending count for header badge
    pending_count = DailyLog.objects.filter(
        intern__internship__supervisor=supervisor_profile,
        status=DailyLogStatus.PENDING
    ).count()

    context = {
        'page_title': 'Intern Daily Logbook',
        'logs': queryset,
        'assigned_interns': assigned_interns,
        'statuses': DailyLogStatus.choices,
        'search_query': search_query,
        'selected_status': selected_status,
        'selected_date': selected_date,
        'selected_intern': selected_intern,
        'pending_count': pending_count,
    }
    return render(request, 'logbook/supervisor_logbook_list.html', context)


@supervisor_required
def supervisor_log_detail_view(request, pk):
    """
    /supervisor/logbook/<id>/
    Full detail of a daily log. Supervisor can submit feedback and approve/reject.
    Only accessible for logs belonging to assigned interns (server-side enforced).
    """
    supervisor_profile = _get_supervisor_profile_or_redirect(request)
    if not supervisor_profile:
        messages.error(request, "Supervisor profile not found.")
        return redirect('supervisor_logbook')

    log = get_object_or_404(DailyLog, pk=pk)

    # Security: ensure log belongs to an intern assigned to this supervisor
    if log.intern.internship.supervisor != supervisor_profile:
        return render(request, '403.html', status=403)

    form = SupervisorFeedbackForm()

    context = {
        'page_title': f'Review Log — {log.intern.user.get_full_name()} ({log.date.strftime("%B %d, %Y")})',
        'log': log,
        'form': form,
    }
    return render(request, 'logbook/supervisor_log_detail.html', context)


@supervisor_required
@require_POST
def supervisor_log_approve_view(request, pk):
    """
    /supervisor/logbook/<id>/approve/  (POST only)
    Transitions log: PENDING → APPROVED.
    Saves optional feedback.
    """
    supervisor_profile = _get_supervisor_profile_or_redirect(request)
    if not supervisor_profile:
        messages.error(request, "Supervisor profile not found.")
        return redirect('supervisor_logbook')

    log = get_object_or_404(DailyLog, pk=pk)

    # Security check
    if log.intern.internship.supervisor != supervisor_profile:
        return render(request, '403.html', status=403)

    if not log.is_pending:
        messages.warning(
            request,
            f"This log is already {log.get_status_display()} and cannot be approved again."
        )
        return redirect('supervisor_log_detail', pk=pk)

    form = SupervisorFeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.cleaned_data.get('feedback', '')
        log.status = DailyLogStatus.APPROVED
        if feedback:
            log.supervisor_feedback = feedback
        log.save()
        messages.success(
            request,
            f"Daily log by {log.intern.user.get_full_name()} ({log.date.strftime('%B %d, %Y')}) "
            f"has been approved."
        )
    else:
        messages.error(request, "An error occurred. Please try again.")

    return redirect('supervisor_logbook')


@supervisor_required
@require_POST
def supervisor_log_reject_view(request, pk):
    """
    /supervisor/logbook/<id>/reject/  (POST only)
    Transitions log: PENDING → REJECTED.
    Supervisor feedback is REQUIRED for rejection.
    """
    supervisor_profile = _get_supervisor_profile_or_redirect(request)
    if not supervisor_profile:
        messages.error(request, "Supervisor profile not found.")
        return redirect('supervisor_logbook')

    log = get_object_or_404(DailyLog, pk=pk)

    # Security check
    if log.intern.internship.supervisor != supervisor_profile:
        return render(request, '403.html', status=403)

    if not log.is_pending:
        messages.warning(
            request,
            f"This log is already {log.get_status_display()} and cannot be rejected again."
        )
        return redirect('supervisor_log_detail', pk=pk)

    form = SupervisorFeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.cleaned_data.get('feedback', '').strip()
        if not feedback:
            messages.error(
                request,
                "Rejection requires supervisor feedback. "
                "Please explain why the log is being rejected so the intern can resubmit."
            )
            return redirect('supervisor_log_detail', pk=pk)

        log.status = DailyLogStatus.REJECTED
        log.supervisor_feedback = feedback
        log.save()
        messages.success(
            request,
            f"Daily log by {log.intern.user.get_full_name()} ({log.date.strftime('%B %d, %Y')}) "
            f"has been rejected. The intern will see your feedback."
        )
    else:
        messages.error(request, "An error occurred. Please try again.")

    return redirect('supervisor_logbook')
