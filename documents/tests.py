import os
import shutil
import tempfile
from datetime import timedelta
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from accounts.models import UserRole
from interns.models import Department, SupervisorProfile, InternProfile, Internship, InternshipStatus
from documents.models import Document, DocumentCategory

User = get_user_model()

# Create a temporary directory for MEDIA_ROOT during tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class DocumentTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()

        # Departments
        self.dept1 = Department.objects.create(name="IT Department")
        self.dept2 = Department.objects.create(name="HR Department")

        # Supervisors
        self.sup1_user = User.objects.create_user(
            email="sup1@test.com", password="password",
            first_name="Supervisor", last_name="One", role=UserRole.SUPERVISOR
        )
        self.sup1 = SupervisorProfile.objects.create(
            user=self.sup1_user, employee_id="EMP-101", department=self.dept1
        )

        self.sup2_user = User.objects.create_user(
            email="sup2@test.com", password="password",
            first_name="Supervisor", last_name="Two", role=UserRole.SUPERVISOR
        )
        self.sup2 = SupervisorProfile.objects.create(
            user=self.sup2_user, employee_id="EMP-102", department=self.dept2
        )

        # Interns
        self.intern1_user = User.objects.create_user(
            email="int1@test.com", password="password",
            first_name="Intern", last_name="One", role=UserRole.INTERN
        )
        self.intern1 = InternProfile.objects.create(
            user=self.intern1_user, intern_id="INT-101", college="Tribhuvan University", program="CSIT"
        )

        self.intern2_user = User.objects.create_user(
            email="int2@test.com", password="password",
            first_name="Intern", last_name="Two", role=UserRole.INTERN
        )
        self.intern2 = InternProfile.objects.create(
            user=self.intern2_user, intern_id="INT-102", college="Kathmandu University", program="SE"
        )

        # Internships
        today = timezone.now().date()
        self.internship1 = Internship.objects.create(
            intern=self.intern1, supervisor=self.sup1, department=self.dept1,
            position="Software Trainee", start_date=today - timedelta(days=30),
            expected_end_date=today + timedelta(days=60), status=InternshipStatus.ACTIVE
        )

        self.internship2 = Internship.objects.create(
            intern=self.intern2, supervisor=self.sup2, department=self.dept2,
            position="HR Assistant", start_date=today - timedelta(days=30),
            expected_end_date=today + timedelta(days=60), status=InternshipStatus.ACTIVE
        )

        # Dummy files
        self.pdf_file = SimpleUploadedFile("sample.pdf", b"%PDF-1.4 test content", content_type="application/pdf")
        self.png_file = SimpleUploadedFile("sample.png", b"\x89PNG\r\n\x1a\n test image", content_type="image/png")

        # Initial Document for Intern 1
        self.doc1 = Document.objects.create(
            intern=self.intern1,
            title="Citizenship Copy",
            category=DocumentCategory.IDENTITY,
            file=self.pdf_file,
            uploaded_by=self.intern1_user,
            description="Front and back copy"
        )

    # -------------------------------------------------------------------------
    # 1. MODEL TESTS
    # -------------------------------------------------------------------------

    def test_document_creation(self):
        """Test document model creation and string representation."""
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(self.doc1.intern, self.intern1)
        self.assertEqual(self.doc1.category, DocumentCategory.IDENTITY)
        self.assertTrue(self.doc1.filename.startswith("sample"))
        self.assertEqual(self.doc1.extension, "pdf")
        self.assertIn("Citizenship Copy", str(self.doc1))

    def test_category_choices(self):
        """Test all category choices can be assigned."""
        categories = [
            DocumentCategory.IDENTITY,
            DocumentCategory.ACADEMIC,
            DocumentCategory.INTERNSHIP_LETTER,
            DocumentCategory.PROJECT_REPORT,
            DocumentCategory.COMPLETION_CERT,
            DocumentCategory.OTHER,
        ]
        for cat in categories:
            doc = Document.objects.create(
                intern=self.intern1,
                title=f"Doc {cat}",
                category=cat,
                file=SimpleUploadedFile(f"{cat}.pdf", b"pdf content", content_type="application/pdf"),
                uploaded_by=self.intern1_user
            )
            self.assertEqual(doc.category, cat)

    # -------------------------------------------------------------------------
    # 2. UPLOAD & VALIDATION TESTS
    # -------------------------------------------------------------------------

    def test_intern_can_upload_valid_pdf(self):
        """Test intern can upload a valid PDF document."""
        self.client.login(email="int1@test.com", password="password")
        file_to_upload = SimpleUploadedFile("transcript.pdf", b"%PDF-1.4 transcript", content_type="application/pdf")
        response = self.client.post(reverse('documents:document_upload'), {
            'title': 'Academic Transcript',
            'category': DocumentCategory.ACADEMIC,
            'file': file_to_upload,
            'description': 'Semester 8 marksheet'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Document.objects.filter(title='Academic Transcript', intern=self.intern1).exists())

    def test_unsupported_file_type_rejected(self):
        """Test unsupported extensions (.exe, .txt) are rejected server-side."""
        self.client.login(email="int1@test.com", password="password")
        bad_file = SimpleUploadedFile("script.exe", b"binary data", content_type="application/x-msdownload")
        response = self.client.post(reverse('documents:document_upload'), {
            'title': 'Bad File',
            'category': DocumentCategory.OTHER,
            'file': bad_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("file", response.context['form'].errors)
        err_msg = str(response.context['form'].errors['file'].as_data()[0].message)
        self.assertIn('File format ".exe" is not supported', err_msg)

    def test_file_over_10mb_rejected(self):
        """Test file larger than 10 MB is rejected server-side."""
        self.client.login(email="int1@test.com", password="password")
        # Create 11 MB dummy file
        large_content = b"0" * (11 * 1024 * 1024)
        large_file = SimpleUploadedFile("huge.pdf", large_content, content_type="application/pdf")
        response = self.client.post(reverse('documents:document_upload'), {
            'title': 'Huge File',
            'category': DocumentCategory.OTHER,
            'file': large_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("exceeds the maximum allowed limit of 10 MB", response.content.decode())

    # -------------------------------------------------------------------------
    # 3. INTERN PERMISSIONS TESTS
    # -------------------------------------------------------------------------

    def test_intern_can_see_own_documents(self):
        """Test intern sees only their own documents on list view."""
        # Create document for Intern 2
        Document.objects.create(
            intern=self.intern2,
            title="Intern 2 Doc",
            category=DocumentCategory.IDENTITY,
            file=SimpleUploadedFile("int2.pdf", b"pdf", content_type="application/pdf"),
            uploaded_by=self.intern2_user
        )

        self.client.login(email="int1@test.com", password="password")
        response = self.client.get(reverse('documents:document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Citizenship Copy")
        self.assertNotContains(response, "Intern 2 Doc")

    def test_intern_cannot_download_another_intern_document(self):
        """Test intern receives 403 when trying to download another intern's document."""
        doc2 = Document.objects.create(
            intern=self.intern2,
            title="Intern 2 Private Doc",
            category=DocumentCategory.ACADEMIC,
            file=SimpleUploadedFile("private.pdf", b"private content", content_type="application/pdf"),
            uploaded_by=self.intern2_user
        )

        self.client.login(email="int1@test.com", password="password")
        response = self.client.get(reverse('documents:document_download', kwargs={'pk': doc2.pk}))
        self.assertEqual(response.status_code, 403)

    def test_intern_can_download_own_document(self):
        """Test intern can download their own document."""
        self.client.login(email="int1@test.com", password="password")
        response = self.client.get(reverse('documents:document_download', kwargs={'pk': self.doc1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_intern_cannot_delete_another_intern_document(self):
        """Test intern receives 403 when trying to delete another intern's document."""
        doc2 = Document.objects.create(
            intern=self.intern2,
            title="Intern 2 Secret Doc",
            category=DocumentCategory.ACADEMIC,
            file=SimpleUploadedFile("secret.pdf", b"secret", content_type="application/pdf"),
            uploaded_by=self.intern2_user
        )

        self.client.login(email="int1@test.com", password="password")
        response = self.client.post(reverse('documents:document_delete', kwargs={'pk': doc2.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Document.objects.filter(pk=doc2.pk).exists())

    def test_intern_can_delete_own_document(self):
        """Test intern can delete their own document via POST."""
        self.client.login(email="int1@test.com", password="password")
        response = self.client.post(reverse('documents:document_delete', kwargs={'pk': self.doc1.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(pk=self.doc1.pk).exists())

    # -------------------------------------------------------------------------
    # 4. SUPERVISOR PERMISSIONS TESTS
    # -------------------------------------------------------------------------

    def test_supervisor_can_see_assigned_intern_documents(self):
        """Test supervisor can see assigned intern documents and not unassigned ones."""
        doc2 = Document.objects.create(
            intern=self.intern2,
            title="Intern 2 Report",
            category=DocumentCategory.PROJECT_REPORT,
            file=SimpleUploadedFile("report.pdf", b"report", content_type="application/pdf"),
            uploaded_by=self.intern2_user
        )

        # Supervisor 1 is assigned to Intern 1, not Intern 2
        self.client.login(email="sup1@test.com", password="password")
        response = self.client.get(reverse('documents:document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Citizenship Copy")
        self.assertNotContains(response, "Intern 2 Report")

    def test_supervisor_can_upload_for_assigned_intern(self):
        """Test supervisor can upload a document on behalf of an assigned intern."""
        self.client.login(email="sup1@test.com", password="password")
        file_to_upload = SimpleUploadedFile("offer.pdf", b"offer letter", content_type="application/pdf")
        response = self.client.post(reverse('documents:document_upload'), {
            'intern': self.intern1.pk,
            'title': 'Official Offer Letter',
            'category': DocumentCategory.INTERNSHIP_LETTER,
            'file': file_to_upload,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        doc = Document.objects.get(title='Official Offer Letter')
        self.assertEqual(doc.intern, self.intern1)
        self.assertEqual(doc.uploaded_by, self.sup1_user)

    def test_supervisor_cannot_upload_for_unassigned_intern(self):
        """Test supervisor cannot upload a document for an unassigned intern."""
        self.client.login(email="sup1@test.com", password="password")
        file_to_upload = SimpleUploadedFile("unassigned.pdf", b"unassigned", content_type="application/pdf")
        response = self.client.post(reverse('documents:document_upload'), {
            'intern': self.intern2.pk,
            'title': 'Unassigned Upload',
            'category': DocumentCategory.OTHER,
            'file': file_to_upload,
        })
        # Form validation rejects intern2 because queryset only contains assigned interns
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(title='Unassigned Upload').exists())

    def test_supervisor_cannot_download_unassigned_intern_document(self):
        """Test supervisor receives 403 when trying to download unassigned intern's document."""
        doc2 = Document.objects.create(
            intern=self.intern2,
            title="Unassigned Intern Doc",
            category=DocumentCategory.OTHER,
            file=SimpleUploadedFile("unassigned.pdf", b"unassigned", content_type="application/pdf"),
            uploaded_by=self.intern2_user
        )

        self.client.login(email="sup1@test.com", password="password")
        response = self.client.get(reverse('documents:document_download', kwargs={'pk': doc2.pk}))
        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_download_assigned_intern_document(self):
        """Test supervisor can download assigned intern's document."""
        self.client.login(email="sup1@test.com", password="password")
        response = self.client.get(reverse('documents:document_download', kwargs={'pk': self.doc1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_supervisor_can_delete_assigned_intern_document(self):
        """Test supervisor can delete assigned intern's document."""
        self.client.login(email="sup1@test.com", password="password")
        response = self.client.post(reverse('documents:document_delete', kwargs={'pk': self.doc1.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(pk=self.doc1.pk).exists())

    # -------------------------------------------------------------------------
    # 5. SECURITY & INTEGRATION TESTS
    # -------------------------------------------------------------------------

    def test_anonymous_access_redirected(self):
        """Test anonymous users are redirected to login page."""
        response = self.client.get(reverse('documents:document_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_delete_requires_post(self):
        """Test GET request to delete endpoint is rejected with 405 Method Not Allowed."""
        self.client.login(email="int1@test.com", password="password")
        response = self.client.get(reverse('documents:document_delete', kwargs={'pk': self.doc1.pk}))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Document.objects.filter(pk=self.doc1.pk).exists())

    def test_filtering_by_category_and_intern(self):
        """Test filtering works on document list view."""
        Document.objects.create(
            intern=self.intern1,
            title="Project Report Draft",
            category=DocumentCategory.PROJECT_REPORT,
            file=SimpleUploadedFile("report.pdf", b"report", content_type="application/pdf"),
            uploaded_by=self.intern1_user
        )

        self.client.login(email="int1@test.com", password="password")

        # Filter by IDENTITY category
        res1 = self.client.get(f"{reverse('documents:document_list')}?category=IDENTITY")
        self.assertContains(res1, "Citizenship Copy")
        self.assertNotContains(res1, "Project Report Draft")

        # Filter by PROJECT_REPORT category
        res2 = self.client.get(f"{reverse('documents:document_list')}?category=PROJECT_REPORT")
        self.assertNotContains(res2, "Citizenship Copy")
        self.assertContains(res2, "Project Report Draft")

    def test_sidebar_navigation_renders_documents_link(self):
        """Test Documents link renders in sidebar navigation for both roles."""
        self.client.login(email="int1@test.com", password="password")
        res1 = self.client.get(reverse('intern_dashboard'))
        self.assertContains(res1, reverse('documents:document_list'))

        self.client.login(email="sup1@test.com", password="password")
        res2 = self.client.get(reverse('supervisor_dashboard'))
        self.assertContains(res2, reverse('documents:document_list'))
