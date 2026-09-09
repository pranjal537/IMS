import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Document, DocumentCategory
from .forms import DocumentUploadForm
from interns.models import InternProfile, SupervisorProfile, Internship


@login_required
def document_list_view(request):
    """
    List uploaded documents based on role:
    - Interns see their own documents.
    - Supervisors see documents belonging to their assigned interns.
    """
    user = request.user
    selected_category = request.GET.get('category', '')
    selected_intern = request.GET.get('intern', '')

    categories = DocumentCategory.choices

    if hasattr(user, 'is_intern') and user.is_intern:
        try:
            intern_profile = user.intern_profile
        except InternProfile.DoesNotExist:
            messages.error(request, _('Intern profile not found.'))
            return redirect('home')

        documents = Document.objects.filter(intern=intern_profile)
        if selected_category:
            documents = documents.filter(category=selected_category)

        context = {
            'documents': documents,
            'categories': categories,
            'selected_category': selected_category,
            'is_intern_view': True,
        }
        return render(request, 'documents/document_list.html', context)

    elif hasattr(user, 'is_supervisor') and user.is_supervisor:
        try:
            supervisor_profile = user.supervisor_profile
        except SupervisorProfile.DoesNotExist:
            messages.error(request, _('Supervisor profile not found.'))
            return redirect('home')

        assigned_internships = Internship.objects.filter(supervisor=supervisor_profile)
        assigned_intern_ids = assigned_internships.values_list('intern_id', flat=True)
        assigned_interns = InternProfile.objects.filter(pk__in=assigned_intern_ids)

        documents = Document.objects.filter(intern_id__in=assigned_intern_ids)

        if selected_intern:
            try:
                intern_id_int = int(selected_intern)
                if intern_id_int in assigned_intern_ids:
                    documents = documents.filter(intern_id=intern_id_int)
                else:
                    documents = Document.objects.none()
            except ValueError:
                pass

        if selected_category:
            documents = documents.filter(category=selected_category)

        context = {
            'documents': documents,
            'assigned_interns': assigned_interns,
            'selected_intern': int(selected_intern) if selected_intern.isdigit() else '',
            'categories': categories,
            'selected_category': selected_category,
            'is_supervisor_view': True,
        }
        return render(request, 'documents/document_list.html', context)

    else:
        raise PermissionDenied(_('Only interns and supervisors can view documents.'))


@login_required
def document_upload_view(request, intern_id=None):
    """
    Upload document view:
    - Intern uploads document for self.
    - Supervisor uploads document on behalf of an assigned intern.
    """
    user = request.user

    if hasattr(user, 'is_intern') and user.is_intern:
        try:
            intern_profile = user.intern_profile
        except InternProfile.DoesNotExist:
            messages.error(request, _('Intern profile not found.'))
            return redirect('home')

        if request.method == 'POST':
            form = DocumentUploadForm(request.POST, request.FILES, user=user)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.intern = intern_profile
                doc.uploaded_by = user
                doc.save()
                messages.success(request, _(f'Document "{doc.title}" uploaded successfully.'))
                return redirect('documents:document_list')
        else:
            form = DocumentUploadForm(user=user)

        context = {
            'form': form,
            'is_intern_view': True,
            'target_intern': intern_profile,
        }
        return render(request, 'documents/document_upload.html', context)

    elif hasattr(user, 'is_supervisor') and user.is_supervisor:
        try:
            supervisor_profile = user.supervisor_profile
        except SupervisorProfile.DoesNotExist:
            messages.error(request, _('Supervisor profile not found.'))
            return redirect('home')

        assigned_internships = Internship.objects.filter(supervisor=supervisor_profile)
        assigned_intern_ids = assigned_internships.values_list('intern_id', flat=True)
        assigned_interns = InternProfile.objects.filter(pk__in=assigned_intern_ids)

        if not assigned_interns.exists():
            messages.warning(request, _('You currently have no assigned interns to upload documents for.'))
            return redirect('documents:document_list')

        initial_data = {}
        if intern_id:
            target_intern = get_object_or_404(InternProfile, pk=intern_id)
            if target_intern not in assigned_interns:
                raise PermissionDenied(_('You are not authorized to upload documents for this intern.'))
            initial_data['intern'] = target_intern

        if request.method == 'POST':
            form = DocumentUploadForm(request.POST, request.FILES, user=user, assigned_interns=assigned_interns)
            if form.is_valid():
                target_intern = form.cleaned_data['intern']
                if target_intern not in assigned_interns:
                    raise PermissionDenied(_('Selected intern is not assigned to you.'))
                doc = form.save(commit=False)
                doc.intern = target_intern
                doc.uploaded_by = user
                doc.save()
                messages.success(request, _(f'Document "{doc.title}" uploaded for {target_intern.user.get_full_name()}.'))
                return redirect('documents:document_list')
        else:
            form = DocumentUploadForm(initial=initial_data, user=user, assigned_interns=assigned_interns)

        context = {
            'form': form,
            'is_supervisor_view': True,
            'assigned_interns': assigned_interns,
        }
        return render(request, 'documents/document_upload.html', context)

    else:
        raise PermissionDenied(_('Only interns and supervisors can upload documents.'))


@login_required
def document_download_view(request, pk):
    """
    Protected document download view:
    - Verifies ownership / assignment before serving file.
    - Prevents direct public access and IDOR vulnerabilities.
    """
    document = get_object_or_404(Document, pk=pk)
    user = request.user

    has_access = False

    if hasattr(user, 'is_intern') and user.is_intern:
        try:
            if document.intern == user.intern_profile:
                has_access = True
        except InternProfile.DoesNotExist:
            pass

    elif hasattr(user, 'is_supervisor') and user.is_supervisor:
        try:
            supervisor_profile = user.supervisor_profile
            is_assigned = Internship.objects.filter(
                supervisor=supervisor_profile,
                intern=document.intern
            ).exists()
            if is_assigned:
                has_access = True
        except SupervisorProfile.DoesNotExist:
            pass

    if not has_access:
        raise PermissionDenied(_('You do not have permission to download this document.'))

    if not document.file or not os.path.isfile(document.file.path):
        raise Http404(_('The requested document file was not found on the server.'))

    response = FileResponse(
        open(document.file.path, 'rb'),
        as_attachment=True,
        filename=document.filename
    )
    return response


@login_required
@require_POST
def document_delete_view(request, pk):
    """
    Protected document deletion view (POST only):
    - Verifies ownership / assignment before deleting.
    - Cleans up file from media storage and deletes DB record.
    """
    document = get_object_or_404(Document, pk=pk)
    user = request.user

    has_access = False

    if hasattr(user, 'is_intern') and user.is_intern:
        try:
            if document.intern == user.intern_profile:
                has_access = True
        except InternProfile.DoesNotExist:
            pass

    elif hasattr(user, 'is_supervisor') and user.is_supervisor:
        try:
            supervisor_profile = user.supervisor_profile
            is_assigned = Internship.objects.filter(
                supervisor=supervisor_profile,
                intern=document.intern
            ).exists()
            if is_assigned:
                has_access = True
        except SupervisorProfile.DoesNotExist:
            pass

    if not has_access:
        raise PermissionDenied(_('You do not have permission to delete this document.'))

    title = document.title

    # Remove physical file if it exists
    if document.file and os.path.isfile(document.file.path):
        try:
            os.remove(document.file.path)
        except OSError:
            pass

    document.delete()
    messages.success(request, _(f'Document "{title}" deleted successfully.'))
    return redirect('documents:document_list')
