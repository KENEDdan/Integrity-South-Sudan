from django.test import TestCase
from django.urls import reverse

from .models import NewsletterSubscriber


class NewsletterSignupTests(TestCase):
    def test_valid_email_subscribes(self):
        response = self.client.post(reverse("contact:newsletter_signup"), {"email": "reader@example.org"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
        self.assertEqual(NewsletterSubscriber.objects.get().email, "reader@example.org")

    def test_duplicate_email_does_not_error_or_duplicate(self):
        NewsletterSubscriber.objects.create(email="reader@example.org")
        response = self.client.post(reverse("contact:newsletter_signup"), {"email": "reader@example.org"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_invalid_email_is_rejected(self):
        response = self.client.post(reverse("contact:newsletter_signup"), {"email": "not-an-email"})
        self.assertEqual(NewsletterSubscriber.objects.count(), 0)

    def test_honeypot_filled_in_is_silently_dropped(self):
        response = self.client.post(reverse("contact:newsletter_signup"), {
            "email": "bot@example.org", "website": "http://spam.example",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NewsletterSubscriber.objects.count(), 0)

    def test_redirects_back_to_the_page_the_form_was_on(self):
        response = self.client.post(reverse("contact:newsletter_signup"), {
            "email": "reader@example.org", "next": "/about/",
        })
        self.assertRedirects(response, "/about/", fetch_redirect_response=False)

    def test_get_request_redirects_home_without_erroring(self):
        response = self.client.get(reverse("contact:newsletter_signup"))
        self.assertEqual(response.status_code, 302)
