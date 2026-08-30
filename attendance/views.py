from django.shortcuts import render

def attendance_placeholder(request):
    """Placeholder view for attendance tracking - Phase 2."""
    return render(request, 'dashboard/supervisor_dashboard.html')
