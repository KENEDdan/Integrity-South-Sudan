import json

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from .models import KoboSubmission

WEBHOOK_SECRET = "test-secret-value"


@override_settings(KOBO_WEBHOOK_SECRET=WEBHOOK_SECRET)
class KoboWebhookTests(TestCase):
    def _post(self, payload, secret=WEBHOOK_SECRET):
        kwargs = {"content_type": "application/json"}
        if secret is not None:
            kwargs["HTTP_X_WEBHOOK_SECRET"] = secret
        return self.client.post(
            reverse("field_data:kobo_webhook"), data=json.dumps(payload), **kwargs
        )

    def test_missing_secret_is_rejected(self):
        response = self._post({"_id": "1", "_xform_id_string": "formA"}, secret=None)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(KoboSubmission.objects.count(), 0)

    def test_wrong_secret_is_rejected(self):
        response = self._post({"_id": "1", "_xform_id_string": "formA"}, secret="wrong")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(KoboSubmission.objects.count(), 0)

    def test_correct_secret_creates_submission(self):
        response = self._post({"_id": "1", "_xform_id_string": "formA", "field": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(KoboSubmission.objects.count(), 1)
        submission = KoboSubmission.objects.get()
        self.assertEqual(submission.form_uid, "formA")
        self.assertEqual(submission.submission_id, "1")

    def test_duplicate_submission_is_not_recreated(self):
        self._post({"_id": "1", "_xform_id_string": "formA"})
        self._post({"_id": "1", "_xform_id_string": "formA"})
        self.assertEqual(KoboSubmission.objects.count(), 1)

    def test_missing_submission_id_is_rejected(self):
        response = self._post({"_xform_id_string": "formA"})
        self.assertEqual(response.status_code, 400)

    def test_get_request_not_allowed(self):
        response = self.client.get(reverse("field_data:kobo_webhook"))
        self.assertEqual(response.status_code, 405)


class SubmissionAccessTests(TestCase):
    def setUp(self):
        self.submission = KoboSubmission.objects.create(
            form_uid="formA", submission_id="1", raw_data={"a": 1},
        )

    def test_anonymous_cannot_view_submissions(self):
        response = self.client.get(reverse("field_data:submission_list"))
        self.assertEqual(response.status_code, 302)

    def test_wrong_role_cannot_view_submissions(self):
        user = User.objects.create_user(username="hruser", password="Str0ng-Pass-9x", role="hr", must_change_password=False)
        self.client.force_login(user)
        response = self.client.get(reverse("field_data:submission_list"))
        self.assertEqual(response.status_code, 403)

    def test_program_manager_can_view_submissions(self):
        user = User.objects.create_user(
            username="pmuser", password="Str0ng-Pass-9x", role="program_manager", must_change_password=False,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("field_data:submission_list"))
        self.assertEqual(response.status_code, 200)
