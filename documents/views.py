from django.shortcuts import render

def documents_placeholder(request):
    """Placeholder view for document management - Phase 2."""
    return render(request, 'dashboard/supervisor_dashboard.html')
