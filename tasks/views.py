from django.shortcuts import render

def tasks_placeholder(request):
    """Placeholder view for tasks - Phase 2."""
    return render(request, 'dashboard/supervisor_dashboard.html')
