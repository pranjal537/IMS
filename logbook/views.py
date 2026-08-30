from django.shortcuts import render

def logbook_placeholder(request):
    """Placeholder view for logbook management - Phase 2."""
    return render(request, 'dashboard/supervisor_dashboard.html')
