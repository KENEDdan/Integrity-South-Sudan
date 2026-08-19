from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import User


def make_user(username, role, **extra):
    user = User.objects.create_user(username=username, password="Str0ng-Pass-9x", role=role, **extra)
    return user


class LoginRequiredTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}")

    def test_login_then_dashboard_succeeds(self):
        user = make_user("plainstaff", "media", must_change_password=False)
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 200)


class RoleRequiredTests(TestCase):
    """apps.accounts.decorators.role_required — access control used across every app."""

    def setUp(self):
        self.hr_user = make_user("hruser", "hr", must_change_password=False)
        self.finance_user = make_user("financeuser", "finance", must_change_password=False)
        self.super_admin = make_user("superadmin", "super_admin", must_change_password=False)

    def test_wrong_role_is_forbidden(self):
        self.client.force_login(self.hr_user)
        response = self.client.get(reverse("accounts:admin_account_list"))
        self.assertEqual(response.status_code, 403)

    def test_matching_role_is_allowed(self):
        self.client.force_login(self.finance_user)
        response = self.client.get(reverse("finance:request_queue"))
        self.assertEqual(response.status_code, 200)

    def test_super_admin_bypasses_every_role_check(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(reverse("accounts:admin_account_list"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_is_redirected_to_login_not_403(self):
        response = self.client.get(reverse("accounts:admin_account_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class ForcePasswordChangeMiddlewareTests(TestCase):
    def setUp(self):
        self.user = make_user("newstaff", "media")  # must_change_password defaults to True
        self.client.force_login(self.user)

    def test_forced_to_password_change_page(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, reverse("accounts:password_change"))

    def test_password_change_page_itself_is_reachable(self):
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 200)

    def test_completing_change_clears_the_flag_and_unlocks_the_app(self):
        response = self.client.post(reverse("accounts:password_change"), {
            "old_password": "Str0ng-Pass-9x",
            "new_password1": "Another-Str0ng-Pass-8y",
            "new_password2": "Another-Str0ng-Pass-8y",
        })
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.user.refresh_from_db()
        self.assertFalse(self.user.must_change_password)


class AdminAccountManagementTests(TestCase):
    def setUp(self):
        self.super_admin = make_user("superadmin", "super_admin", must_change_password=False)
        self.client.force_login(self.super_admin)

    def test_creating_account_sets_temp_password_and_forces_change(self):
        response = self.client.post(reverse("accounts:admin_account_create"), {
            "username": "newhire", "first_name": "New", "last_name": "Hire",
            "email": "newhire@example.org", "phone_number": "", "role": "hr",
        })
        self.assertEqual(response.status_code, 200)
        account = User.objects.get(username="newhire")
        self.assertTrue(account.must_change_password)
        self.assertTrue(account.check_password(response.context["temp_password"]))

    def test_cannot_deactivate_own_account(self):
        response = self.client.post(
            reverse("accounts:admin_account_toggle_active", args=[self.super_admin.pk]),
            follow=True,
        )
        self.super_admin.refresh_from_db()
        self.assertTrue(self.super_admin.is_active)
        self.assertContains(response, "can&#x27;t deactivate your own account")

    def test_non_super_admin_cannot_create_accounts(self):
        hr_user = make_user("hruser", "hr", must_change_password=False)
        self.client.force_login(hr_user)
        response = self.client.get(reverse("accounts:admin_account_create"))
        self.assertEqual(response.status_code, 403)

    def test_creating_account_emails_the_temp_password_to_the_new_address(self):
        self.client.post(reverse("accounts:admin_account_create"), {
            "username": "newhire2", "first_name": "New", "last_name": "Hire",
            "email": "newhire2@example.org", "phone_number": "", "role": "hr",
        })
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ["newhire2@example.org"])
        account = User.objects.get(username="newhire2")
        self.assertIn(account.username, sent.body)

    def test_reset_password_emails_the_account(self):
        target = make_user("resetme", "hr", must_change_password=False)
        target.email = "resetme@example.org"
        target.save()
        self.client.post(reverse("accounts:admin_account_reset_password", args=[target.pk]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["resetme@example.org"])


class LoginLockoutTests(TestCase):
    """django-axes: repeated failed logins should lock out the account/IP."""

    def setUp(self):
        make_user("targetuser", "hr", must_change_password=False)

    def test_correct_password_still_works_before_lockout(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "targetuser", "password": "Str0ng-Pass-9x",
        })
        self.assertRedirects(response, reverse("accounts:dashboard"), fetch_redirect_response=False)

    def test_repeated_wrong_passwords_lock_out_further_attempts(self):
        for _ in range(5):
            self.client.post(reverse("accounts:login"), {
                "username": "targetuser", "password": "wrong-password",
            })
        # Even the correct password should now be refused — the account/IP is locked.
        response = self.client.post(reverse("accounts:login"), {
            "username": "targetuser", "password": "Str0ng-Pass-9x",
        })
        self.assertNotEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
