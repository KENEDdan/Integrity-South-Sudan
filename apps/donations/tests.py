from django.test import TestCase
from django.urls import reverse

from .models import Donation

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
