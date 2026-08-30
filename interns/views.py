from django.shortcuts import render
from django.http import HttpResponse

def intern_list_placeholder(request):
    """Placeholder view for intern list - Phase 2."""
    return render(request, 'dashboard/supervisor_dashboard.html')
