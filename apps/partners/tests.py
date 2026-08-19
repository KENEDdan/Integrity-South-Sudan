from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import PartnerRequest

VALID_FIELDS = {
    "organization_name": "Example NGO",
    "address": "123 Main St, Juba",
    "contact_email": "contact@example.org",
    "contact_phone": "",
    "reason": "We would like to partner on civic education.",
    "contract_validity": "",
}


class PublicPartnerRequestUploadTests(TestCase):
    """apps/partners/models.py PartnerRequest.registration_documents — the one fully
    public, unauthenticated file-upload endpoint in the app."""

    def _post(self, **files):
        return self.client.post(reverse("partners:partner_request_create"), {**VALID_FIELDS, **files})

    def test_html_disguised_as_a_document_is_rejected(self):
        malicious = SimpleUploadedFile(
            "resume.html", b"<script>alert(document.cookie)</script>", content_type="text/html",
        )
        response = self._post(registration_documents=malicious)
        self.assertEqual(response.status_code, 200)  # re-renders form with errors, not a redirect
        self.assertEqual(PartnerRequest.objects.count(), 0)
        self.assertContains(response, "not allowed")

    def test_oversized_document_is_rejected(self):
        too_big = SimpleUploadedFile(
            "registration.pdf", b"x" * (11 * 1024 * 1024), content_type="application/pdf",
        )
        response = self._post(registration_documents=too_big)
        self.assertEqual(PartnerRequest.objects.count(), 0)
        self.assertContains(response, "too large")

    def test_legitimate_pdf_is_accepted(self):
        legit = SimpleUploadedFile("registration.pdf", b"%PDF-1.4 fake but small", content_type="application/pdf")
        response = self._post(registration_documents=legit)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PartnerRequest.objects.count(), 1)

    def test_request_with_no_documents_still_works(self):
        response = self._post()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PartnerRequest.objects.count(), 1)

    def test_honeypot_filled_in_is_silently_dropped(self):
        response = self.client.post(reverse("partners:partner_request_create"), {
            **VALID_FIELDS, "website": "http://spam.example",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PartnerRequest.objects.count(), 0)
