"""
Views for Damak Municipality Intern Management System (IMS).
Phase 2: Authentication & Role-Based Access Control.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings
from django.utils import timezone
import django
import sys

from .forms import LoginForm, ImsPasswordChangeForm
from .decorators import supervisor_required, intern_required


# ─── Public Views ────────────────────────────────────────────────────────────

def home_view(request):
    """
    Landing page for Damak Municipality IMS.
    Authenticated users see a redirect prompt to their dashboard.
    """
    return render(request, 'home.html')


def login_view(request):
    """
    Email + password login using Django's authentication system.
    Redirects to role-appropriate dashboard on success.
    Does not reveal whether an email exists (generic error).
    """
    # Redirect already-authenticated users to their dashboard
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request,
                f"Welcome back, {user.get_short_name() or user.email}! "
                f"You are logged in as {user.get_role_display()}."
            )
            # Honour ?next= redirect parameter if present and safe
            next_url = request.GET.get('next', '')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('dashboard_redirect')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Secure logout: clears Django session, redirects to login.
    Accepts both GET and POST for convenience but works correctly either way.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# ─── Dashboard Routing ────────────────────────────────────────────────────────

@login_required
def dashboard_redirect_view(request):
    """
    Generic /dashboard/ endpoint — redirects the authenticated user
    to the correct role-specific dashboard.
    """
    if request.user.is_supervisor:
        return redirect('supervisor_dashboard')
    elif request.user.is_intern:
        return redirect('intern_dashboard')
    # Fallback (should not happen with well-formed roles)
    return redirect('home')


# ─── Supervisor Views ─────────────────────────────────────────────────────────

@supervisor_required
def supervisor_dashboard_view(request):
    """
    Supervisor-only dashboard.
    Enforces role access and displays attendance overview for assigned interns.
    """
    supervisor_profile = getattr(request.user, 'supervisor_profile', None)
    today = timezone.now().date()

    assigned_count = 0
    present_today = 0
    leave_today = 0
    absent_today = 0
    today_records = []
    pending_log_count = 0
    recent_pending_logs = []

    if supervisor_profile:
        assigned_interns = supervisor_profile.assigned_internships.all()
        assigned_count = assigned_interns.count()

        from attendance.models import Attendance, AttendanceStatus
        today_qs = Attendance.objects.filter(
            intern__internship__supervisor=supervisor_profile,
            date=today
        ).select_related('intern', 'intern__user')

        present_today = today_qs.filter(status=AttendanceStatus.PRESENT).count()
        leave_today = today_qs.filter(status=AttendanceStatus.LEAVE).count()
        absent_today = today_qs.filter(status=AttendanceStatus.ABSENT).count()
        today_records = today_qs

        # Phase 5: Logbook pending logs for supervisor dashboard
        from logbook.models import DailyLog, DailyLogStatus
        pending_log_count = DailyLog.objects.filter(
            intern__internship__supervisor=supervisor_profile,
            status=DailyLogStatus.PENDING
        ).count()
        recent_pending_logs = DailyLog.objects.filter(
            intern__internship__supervisor=supervisor_profile,
            status=DailyLogStatus.PENDING
        ).select_related('intern', 'intern__user').order_by('-date')[:5]

    context = {
        'page_title': 'Supervisor Dashboard',
        'welcome_name': request.user.get_full_name() or request.user.email,
        'assigned_count': assigned_count,
        'present_today': present_today,
        'leave_today': leave_today,
        'absent_today': absent_today,
        'today_records': today_records,
        'today_date': today,
        'pending_log_count': pending_log_count,
        'recent_pending_logs': recent_pending_logs,
    }
    return render(request, 'dashboard/supervisor_dashboard.html', context)


# ─── Intern Views ─────────────────────────────────────────────────────────────

@intern_required
def intern_dashboard_view(request):
    """
    Intern-only dashboard.
    Enforces role access and displays attendance metrics and recent log.
    """
    intern_profile = getattr(request.user, 'intern_profile', None)
    today = timezone.now().date()

    stats = None
    today_record = None
    recent_records = []
    log_stats = None
    latest_log = None

    if intern_profile:
        from attendance.utils import calculate_intern_attendance_stats
        from attendance.models import Attendance
        stats = calculate_intern_attendance_stats(intern_profile)
        today_record = Attendance.objects.filter(intern=intern_profile, date=today).first()
        recent_records = Attendance.objects.filter(intern=intern_profile).order_by('-date')[:5]

        # Phase 5: Logbook stats for intern dashboard
        from logbook.views import calculate_intern_log_stats
        from logbook.models import DailyLog
        log_stats = calculate_intern_log_stats(intern_profile)
        latest_log = DailyLog.objects.filter(intern=intern_profile).order_by('-date').first()

    context = {
        'page_title': 'Intern Dashboard',
        'welcome_name': request.user.get_full_name() or request.user.email,
        'stats': stats,
        'today_record': today_record,
        'recent_records': recent_records,
        'today_date': today,
        'log_stats': log_stats,
        'latest_log': latest_log,
    }
    return render(request, 'dashboard/intern_dashboard.html', context)


# ─── Password Management ──────────────────────────────────────────────────────

@login_required
def password_change_view(request):
    """
    Password change page using Django's PasswordChangeForm.
    Keeps the user logged in after a successful change.
    """
    if request.method == 'POST':
        form = ImsPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session so the user stays logged in
            update_session_auth_hash(request, user)
            messages.success(
                request,
                "Your password has been changed successfully. "
                "You are still logged in."
            )
            return redirect('dashboard_redirect')
        else:
            messages.error(
                request,
                "Please correct the errors below."
            )
    else:
        form = ImsPasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})


# ─── System Health ────────────────────────────────────────────────────────────

def health_view(request):
    """System health check and diagnostic test page."""
    db_engine = django_settings.DATABASES['default']['ENGINE'].split('.')[-1]
    db_name = django_settings.DATABASES['default'].get('NAME', 'N/A')

    context = {
        'system_status': 'Operational',
        'django_version': django.get_version(),
        'python_version': sys.version.split()[0],
        'db_engine': db_engine,
        'db_name': str(db_name),
        'debug_mode': django_settings.DEBUG,
        'timezone': str(django_settings.TIME_ZONE),
        'server_time': timezone.now(),
        'installed_apps_count': len(django_settings.INSTALLED_APPS),
        'ims_apps': [
            'accounts', 'interns', 'attendance', 'logbook',
            'tasks', 'evaluations', 'documents'
        ]
    }
    return render(request, 'health.html', context)
