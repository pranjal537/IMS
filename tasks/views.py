from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import supervisor_required, intern_required
from .models import Task, TaskPriority, TaskStatus
from .forms import SupervisorTaskForm, SupervisorTaskEditForm, InternTaskProgressForm
from interns.models import InternProfile

# -----------------------------------------
# SUPERVISOR VIEWS
# -----------------------------------------

@supervisor_required
def supervisor_task_list_view(request):
    supervisor_profile = request.user.supervisor_profile
    tasks = Task.objects.filter(intern__internship__supervisor=supervisor_profile)
    
    # Search
    q = request.GET.get('q', '').strip()
    if q:
        tasks = tasks.filter(
            Q(title__icontains=q) |
            Q(intern__user__first_name__icontains=q) |
            Q(intern__user__last_name__icontains=q) |
            Q(intern__intern_id__icontains=q)
        )
    
    # Filters
    intern_id = request.GET.get('intern', '').strip()
    if intern_id:
        tasks = tasks.filter(intern__intern_id=intern_id)
        
    priority = request.GET.get('priority', '').strip()
    if priority:
        tasks = tasks.filter(priority=priority)
        
    status = request.GET.get('status', '').strip()
    # Handle overdue logic correctly for filter
    if status == TaskStatus.OVERDUE:
        from django.utils import timezone
        tasks = tasks.filter(
            due_date__lt=timezone.now().date()
        ).exclude(status=TaskStatus.COMPLETED)
    elif status:
        tasks = tasks.filter(status=status)
        
    # Interns assigned to supervisor for filter dropdown
    interns = InternProfile.objects.filter(internship__supervisor=supervisor_profile).select_related('user')
        
    context = {
        'tasks': tasks,
        'interns': interns,
        'priorities': TaskPriority.choices,
        'statuses': TaskStatus.choices,
        'page_title': 'Intern Tasks',
    }
    return render(request, 'tasks/supervisor_task_list.html', context)

@supervisor_required
def supervisor_task_create_view(request):
    supervisor_profile = request.user.supervisor_profile
    
    if request.method == 'POST':
        form = SupervisorTaskForm(request.POST, supervisor_profile=supervisor_profile)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = supervisor_profile
            task.status = TaskStatus.PENDING
            task.progress = 0
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('supervisor_task_list')
    else:
        form = SupervisorTaskForm(supervisor_profile=supervisor_profile)
        
    context = {
        'form': form,
        'page_title': 'Create Task',
    }
    return render(request, 'tasks/supervisor_task_form.html', context)

@supervisor_required
def supervisor_task_detail_view(request, pk):
    supervisor_profile = request.user.supervisor_profile
    task = get_object_or_404(Task, pk=pk, intern__internship__supervisor=supervisor_profile)
    
    context = {
        'task': task,
        'page_title': f'Task: {task.title}',
    }
    return render(request, 'tasks/supervisor_task_detail.html', context)

@supervisor_required
def supervisor_task_edit_view(request, pk):
    supervisor_profile = request.user.supervisor_profile
    task = get_object_or_404(Task, pk=pk, intern__internship__supervisor=supervisor_profile)
    
    if request.method == 'POST':
        form = SupervisorTaskEditForm(request.POST, instance=task, supervisor_profile=supervisor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('supervisor_task_detail', pk=task.pk)
    else:
        form = SupervisorTaskEditForm(instance=task, supervisor_profile=supervisor_profile)
        
    context = {
        'form': form,
        'task': task,
        'page_title': f'Edit Task: {task.title}',
    }
    return render(request, 'tasks/supervisor_task_form.html', context)


# -----------------------------------------
# INTERN VIEWS
# -----------------------------------------

@intern_required
def intern_task_list_view(request):
    intern_profile = request.user.intern_profile
    tasks = Task.objects.filter(intern=intern_profile)
    
    # Search
    q = request.GET.get('q', '').strip()
    if q:
        tasks = tasks.filter(title__icontains=q)
        
    # Filters
    priority = request.GET.get('priority', '').strip()
    if priority:
        tasks = tasks.filter(priority=priority)
        
    status = request.GET.get('status', '').strip()
    if status == TaskStatus.OVERDUE:
        from django.utils import timezone
        tasks = tasks.filter(
            due_date__lt=timezone.now().date()
        ).exclude(status=TaskStatus.COMPLETED)
    elif status:
        tasks = tasks.filter(status=status)
        
    context = {
        'tasks': tasks,
        'priorities': TaskPriority.choices,
        'statuses': TaskStatus.choices,
        'page_title': 'My Tasks',
    }
    return render(request, 'tasks/intern_task_list.html', context)

@intern_required
def intern_task_detail_view(request, pk):
    intern_profile = request.user.intern_profile
    task = get_object_or_404(Task, pk=pk, intern=intern_profile)
    
    if request.method == 'POST':
        form = InternTaskProgressForm(request.POST, instance=task)
        if form.is_valid():
            # Only update status and progress based on form
            # Automatic status transitions based on progress
            updated_task = form.save(commit=False)
            
            # Additional layer to ensure consistent state
            if updated_task.progress == 100:
                updated_task.status = TaskStatus.COMPLETED
            elif updated_task.progress > 0 and updated_task.status == TaskStatus.PENDING:
                updated_task.status = TaskStatus.IN_PROGRESS
                
            updated_task.save()
            messages.success(request, 'Task progress updated.')
            return redirect('intern_task_detail', pk=task.pk)
    else:
        form = InternTaskProgressForm(instance=task)
        
    context = {
        'task': task,
        'form': form,
        'page_title': f'Task: {task.title}',
    }
    return render(request, 'tasks/intern_task_detail.html', context)
