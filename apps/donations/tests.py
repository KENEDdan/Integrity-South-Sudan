from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, User
from apps.finance.models import FinanceBalance, Transaction
from .models import Donation, DonationStatus

VALID_FIELDS = {
    "donor_name": "Jane Donor",
    "donor_email": "jane@example.org",
    "donor_phone": "",
    "amount": "25.00",
    "currency": "USD",
    "frequency": "one_time",
    "message": "",
}


class DonationHoneypotTests(TestCase):
    def test_normal_submission_is_saved(self):
        response = self.client.post(reverse("donations:donate"), VALID_FIELDS)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Donation.objects.count(), 1)

    def test_honeypot_filled_in_is_silently_dropped(self):
        response = self.client.post(reverse("donations:donate"), {**VALID_FIELDS, "website": "http://spam.example"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Donation.objects.count(), 0)


class DonationAmountValidationTests(TestCase):
    def test_zero_amount_is_rejected(self):
        response = self.client.post(reverse("donations:donate"), {**VALID_FIELDS, "amount": "0"})
        self.assertEqual(response.status_code, 200)  # re-renders the form, doesn't redirect
        self.assertEqual(Donation.objects.count(), 0)
        self.assertContains(response, "greater than or equal to")

    def test_negative_amount_is_rejected(self):
        response = self.client.post(reverse("donations:donate"), {**VALID_FIELDS, "amount": "-10"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Donation.objects.count(), 0)
        self.assertContains(response, "greater than or equal to")


class DonationThanksLookupTests(TestCase):
    def setUp(self):
        self.response = self.client.post(reverse("donations:donate"), VALID_FIELDS)
        self.donation = Donation.objects.get(donor_email=VALID_FIELDS["donor_email"])

    def test_thanks_redirect_uses_reference_code_not_pk(self):
        self.assertEqual(self.response["Location"], reverse(
            "donations:donate_thanks", kwargs={"reference_code": self.donation.reference_code},
        ))

    def test_sequential_pk_no_longer_resolves(self):
        response = self.client.get(f"/donate/thanks/{self.donation.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_thanks_page_loads_by_reference_code(self):
        response = self.client.get(self.response["Location"])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.donation.reference_code)


class DonationProofOfPaymentTests(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(**{**VALID_FIELDS, "amount": "25.00"})
        self.thanks_url = reverse("donations:donate_thanks", kwargs={"reference_code": self.donation.reference_code})
        self.finance_user = User.objects.create_user(
            username="finance_reviewer", password="not-a-real-password-123", role=Role.FINANCE,
            must_change_password=False,
        )

    def _upload(self, filename="receipt.pdf"):
        proof = SimpleUploadedFile(filename, b"%PDF-1.4 fake receipt", content_type="application/pdf")
        return self.client.post(self.thanks_url, {"proof_of_payment": proof})

    def test_donor_can_upload_proof_of_payment(self):
        response = self._upload()
        self.assertEqual(response.status_code, 302)
        self.donation.refresh_from_db()
        self.assertTrue(self.donation.proof_of_payment)
        self.assertIsNotNone(self.donation.proof_uploaded_at)
        self.assertEqual(self.donation.status, DonationStatus.PENDING)

    def test_anonymous_cannot_download_proof(self):
        self._upload()
        response = self.client.get(reverse("donations:donation_proof_download", args=[self.donation.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_finance_can_download_proof(self):
        self._upload()
        self.client.force_login(self.finance_user)
        response = self.client.get(reverse("donations:donation_proof_download", args=[self.donation.pk]))
        self.assertEqual(response.status_code, 200)

    def test_finance_reject_lets_donor_resubmit(self):
        self._upload()
        self.client.force_login(self.finance_user)
        response = self.client.post(reverse("donations:donation_confirm", args=[self.donation.pk]), {"reject": "1"})
        self.assertEqual(response.status_code, 302)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, DonationStatus.REJECTED)

        self.client.logout()
        response = self._upload(filename="receipt2.pdf")
        self.assertEqual(response.status_code, 302)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, DonationStatus.PENDING)

    def test_finance_confirm_records_income_and_updates_balance(self):
        self._upload()
        balance_before = FinanceBalance.get_solo().bank_usd
        self.client.force_login(self.finance_user)
        response = self.client.post(reverse("donations:donation_confirm", args=[self.donation.pk]), {"confirm": "1"})
        self.assertEqual(response.status_code, 302)

        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, DonationStatus.CONFIRMED)
        self.assertEqual(self.donation.confirmed_by, self.finance_user)

        balance_after = FinanceBalance.get_solo().bank_usd
        self.assertEqual(balance_after - balance_before, self.donation.amount)
        self.assertTrue(Transaction.objects.filter(description__contains=self.donation.reference_code).exists())
