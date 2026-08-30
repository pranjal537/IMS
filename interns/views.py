from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden

from accounts.decorators import supervisor_required, intern_required
from .models import Department, SupervisorProfile, InternProfile, Internship, InternshipStatus
from .forms import DepartmentForm, SupervisorProfileEditForm, InternProfileEditForm, InternshipForm
from .utils import calculate_internship_progress


# ─── Supervisor Views ─────────────────────────────────────────────────────────

@supervisor_required
def supervisor_my_interns_view(request):
    """
    Supervisor's My Interns page.
    Restricted strictly to the logged-in supervisor's assigned interns.
    Includes search and filtering by status and department.
    """
    supervisor_profile = getattr(request.user, 'supervisor_profile', None)
    if not supervisor_profile:
        messages.warning(request, "Supervisor profile not found. Please contact an administrator.")
        return render(request, 'interns/supervisor_my_interns.html', {
            'internships_data': [],
            'departments': Department.objects.all(),
            'statuses': InternshipStatus.choices,
        })

    # Only fetch internships belonging to THIS supervisor
    queryset = Internship.objects.filter(supervisor=supervisor_profile).select_related(
        'intern', 'intern__user', 'department'
    )

    # Search filtering
    search_query = request.GET.get('q', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(intern__user__first_name__icontains=search_query) |
            Q(intern__user__last_name__icontains=search_query) |
            Q(intern__user__email__icontains=search_query) |
            Q(intern__intern_id__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    # Status filtering
    selected_status = request.GET.get('status', '').strip()
    if selected_status:
        queryset = queryset.filter(status=selected_status)

    # Department filtering
    selected_department = request.GET.get('department', '').strip()
    if selected_department:
        queryset = queryset.filter(department_id=selected_department)

    # Attach progress metrics to each internship
    internships_data = []
    for item in queryset:
        metrics = calculate_internship_progress(item)
        internships_data.append({
            'internship': item,
            'metrics': metrics,
        })

    context = {
        'page_title': 'My Interns',
        'internships_data': internships_data,
        'departments': Department.objects.all(),
        'statuses': InternshipStatus.choices,
        'search_query': search_query,
        'selected_status': selected_status,
        'selected_department': selected_department,
    }
    return render(request, 'interns/supervisor_my_interns.html', context)


@supervisor_required
def supervisor_profile_view(request):
    """View and edit supervisor profile."""
    profile, created = SupervisorProfile.objects.get_or_create(
        user=request.user,
        defaults={'employee_id': f"EMP-{request.user.id:03d}"}
    )

    if request.method == 'POST':
        form = SupervisorProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your supervisor profile has been updated successfully.")
            return redirect('interns:supervisor_profile')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = SupervisorProfileEditForm(instance=profile)

    context = {
        'page_title': 'Supervisor Profile',
        'profile': profile,
        'form': form,
    }
    return render(request, 'interns/supervisor_profile.html', context)


# ─── Intern Views ─────────────────────────────────────────────────────────────

@intern_required
def intern_my_internship_view(request):
    """
    Intern's My Internship page.
    Shows intern profile details, supervisor, department, dates, working day calculation, and progress.
    """
    intern_profile = getattr(request.user, 'intern_profile', None)
    if not intern_profile:
        messages.warning(request, "Intern profile not found. Please contact an administrator.")
        return render(request, 'interns/intern_my_internship.html', {'internship': None, 'metrics': None})

    try:
        internship = Internship.objects.select_related('supervisor', 'supervisor__user', 'department').get(intern=intern_profile)
        metrics = calculate_internship_progress(internship)
    except Internship.DoesNotExist:
        internship = None
        metrics = None

    context = {
        'page_title': 'My Internship',
        'intern_profile': intern_profile,
        'internship': internship,
        'metrics': metrics,
    }
    return render(request, 'interns/intern_my_internship.html', context)


@intern_required
def intern_profile_view(request):
    """
    View and edit intern personal profile.
    Protected fields (intern_id, supervisor, dates, status) are immutable.
    """
    profile, created = InternProfile.objects.get_or_create(
        user=request.user,
        defaults={'intern_id': InternProfile.generate_next_intern_id()}
    )

    if request.method == 'POST':
        form = InternProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('interns:intern_profile')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = InternProfileEditForm(instance=profile)

    # Get internship details if present
    internship = getattr(profile, 'internship', None)

    context = {
        'page_title': 'My Profile',
        'profile': profile,
        'form': form,
        'internship': internship,
    }
    return render(request, 'interns/intern_profile.html', context)


# ─── Department Management (Staff / Superuser) ───────────────────────────────

@staff_member_required
def department_list_view(request):
    """List all departments (Staff management)."""
    departments = Department.objects.all()
    return render(request, 'interns/department_list.html', {
        'departments': departments,
        'page_title': 'Departments Management',
    })


@staff_member_required
def department_create_view(request):
    """Create a new department."""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect('interns:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'interns/department_form.html', {
        'form': form,
        'title': 'Create Department',
        'page_title': 'Create Department',
    })


@staff_member_required
def department_edit_view(request, pk):
    """Edit an existing department."""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect('interns:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'interns/department_form.html', {
        'form': form,
        'department': department,
        'title': f'Edit Department: {department.name}',
        'page_title': 'Edit Department',
    })


@staff_member_required
def department_delete_view(request, pk):
    """Delete a department."""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' deleted successfully.")
        return redirect('interns:department_list')
    return render(request, 'interns/department_confirm_delete.html', {
        'department': department,
        'page_title': 'Delete Department',
    })
