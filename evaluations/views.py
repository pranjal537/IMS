from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg

from accounts.decorators import supervisor_required, intern_required
from interns.models import Internship
from interns.utils import calculate_internship_progress
from attendance.utils import calculate_intern_attendance_stats
from logbook.models import DailyLog, DailyLogStatus
from logbook.views import calculate_intern_log_stats
from attendance.models import Attendance, AttendanceStatus
from tasks.models import Task, TaskStatus
from .models import Evaluation
from .forms import EvaluationForm

# ---------------------------------------------------------
# SUPERVISOR VIEWS
# ---------------------------------------------------------

@supervisor_required
def supervisor_evaluation_list(request):
    supervisor_profile = request.user.supervisor_profile
    internships = Internship.objects.filter(supervisor=supervisor_profile).select_related('intern__user', 'evaluation')
    
    context = {
        'internships': internships,
        'page_title': 'Intern Evaluations',
    }
    return render(request, 'evaluations/supervisor_evaluation_list.html', context)


@supervisor_required
def supervisor_evaluation_detail(request, pk):
    supervisor_profile = request.user.supervisor_profile
    evaluation = get_object_or_404(Evaluation, pk=pk, internship__supervisor=supervisor_profile)
    
    context = {
        'evaluation': evaluation,
        'page_title': f"Evaluation: {evaluation.internship.intern.user.get_full_name()}",
    }
    return render(request, 'evaluations/supervisor_evaluation_detail.html', context)


@supervisor_required
def supervisor_evaluation_create(request, internship_id):
    supervisor_profile = request.user.supervisor_profile
    internship = get_object_or_404(Internship, pk=internship_id, supervisor=supervisor_profile)
    
    if hasattr(internship, 'evaluation'):
        messages.warning(request, 'Evaluation already exists for this intern.')
        return redirect('evaluations:supervisor_evaluation_detail', pk=internship.evaluation.pk)
        
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.internship = internship
            evaluation.save()
            messages.success(request, 'Evaluation created successfully.')
            return redirect('evaluations:supervisor_evaluation_detail', pk=evaluation.pk)
    else:
        form = EvaluationForm()
        
    # Basic progress data for context during evaluation
    total_tasks = Task.objects.filter(intern=internship.intern).count()
    completed_tasks = Task.objects.filter(intern=internship.intern, status=TaskStatus.COMPLETED).count()
    total_logs = DailyLog.objects.filter(intern=internship.intern).count()
    approved_logs = DailyLog.objects.filter(intern=internship.intern, status=DailyLogStatus.APPROVED).count()
        
    context = {
        'form': form,
        'internship': internship,
        'page_title': f"Evaluate: {internship.intern.user.get_full_name()}",
        'progress_context': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'total_logs': total_logs,
            'approved_logs': approved_logs
        }
    }
    return render(request, 'evaluations/supervisor_evaluation_form.html', context)


@supervisor_required
def supervisor_evaluation_edit(request, pk):
    supervisor_profile = request.user.supervisor_profile
    evaluation = get_object_or_404(Evaluation, pk=pk, internship__supervisor=supervisor_profile)
    
    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluation updated successfully.')
            return redirect('evaluations:supervisor_evaluation_detail', pk=evaluation.pk)
    else:
        form = EvaluationForm(instance=evaluation)
        
    context = {
        'form': form,
        'internship': evaluation.internship,
        'page_title': f"Edit Evaluation: {evaluation.internship.intern.user.get_full_name()}",
    }
    return render(request, 'evaluations/supervisor_evaluation_form.html', context)


# ---------------------------------------------------------
# INTERN VIEWS
# ---------------------------------------------------------

@intern_required
def intern_evaluation_detail(request):
    intern_profile = request.user.intern_profile
    internship = get_object_or_404(Internship, intern=intern_profile)
    
    evaluation = getattr(internship, 'evaluation', None)
    
    context = {
        'evaluation': evaluation,
        'internship': internship,
        'page_title': 'My Evaluation',
    }
    return render(request, 'evaluations/intern_evaluation_detail.html', context)


@intern_required
def intern_progress(request):
    intern_profile = request.user.intern_profile
    internship = get_object_or_404(Internship, intern=intern_profile)
    
    # 1. Internship Progress — uses working-day calculation (Mon–Fri)
    time_stats = calculate_internship_progress(internship)
    
    # 2. Attendance — uses working-day calculation
    attendance_stats = calculate_intern_attendance_stats(intern_profile)
    
    # 3. Daily Logs — reuse existing helper
    log_stats = calculate_intern_log_stats(intern_profile)
    
    # 4. Tasks
    tasks = Task.objects.filter(intern=intern_profile)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status=TaskStatus.COMPLETED).count()
    avg_task_progress = tasks.aggregate(Avg('progress'))['progress__avg'] or 0
    
    context = {
        'internship': internship,
        'evaluation': getattr(internship, 'evaluation', None),
        
        'time_stats': {
            'total_days': time_stats['total_working_days'],
            'days_completed': time_stats['completed_working_days'],
            'remaining_days': time_stats['remaining_working_days'],
            'progress_pct': time_stats['progress_percentage'],
        },
        'attendance_stats': {
            'total': attendance_stats['total_working_days'],
            'present': attendance_stats['present_days'],
            'leave': attendance_stats['leave_days'],
            'absent': attendance_stats['absent_days'],
            'pct': attendance_stats['attendance_percentage'],
        },
        'log_stats': {
            'total': log_stats['total'],
            'approved': log_stats['approved'],
            'pending': log_stats['pending'],
            'rejected': log_stats['rejected'],
            'total_hours': log_stats['total_hours'],
        },
        'task_stats': {
            'total': total_tasks,
            'completed': completed_tasks,
            'avg_progress': int(avg_task_progress),
        },
        'page_title': 'My Internship Progress',
    }
    return render(request, 'evaluations/intern_progress.html', context)
