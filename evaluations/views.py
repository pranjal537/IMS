from django.shortcuts import render

def evaluations_placeholder(request):
    """Placeholder view for evaluations - Phase 2."""
    return render(request, 'dashboard/supervisor_dashboard.html')
