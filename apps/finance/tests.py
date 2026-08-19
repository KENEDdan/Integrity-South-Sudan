from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from .models import FinanceBalance, FinancialRequest, FinancialRequestStatus, Transaction


def make_user(username, role):
    return User.objects.create_user(username=username, password="Str0ng-Pass-9x", role=role, must_change_password=False)


class FinanceBalanceConcurrencyTests(TestCase):
    """FinanceBalance.apply() must do a DB-level increment, not a Python
    read-modify-write, or two near-simultaneous transactions can lose one
    update. Simulated here by loading two stale in-memory copies first."""

    def test_apply_does_not_lose_updates_from_a_stale_in_memory_copy(self):
        FinanceBalance.get_solo()
        stale_copy_a = FinanceBalance.objects.get(pk=1)
        stale_copy_b = FinanceBalance.objects.get(pk=1)

        stale_copy_a.apply("cash", "USD", Decimal("100.00"))
        stale_copy_b.apply("cash", "USD", Decimal("50.00"))  # loaded before A's update

        balance = FinanceBalance.get_solo()
        self.assertEqual(balance.cash_usd, Decimal("150.00"))


class FinancialRequestLifecycleTests(TestCase):
    """The four-eyes approval chain: requester -> finance -> super_admin -> finance disburses."""

    def setUp(self):
        self.requester = make_user("media1", "media")
        self.finance = make_user("finance1", "finance")
        self.super_admin = make_user("admin1", "super_admin")

    def _login(self, user):
        self.client.logout()
        self.client.force_login(user)

    def test_full_approval_and_disbursement_updates_balance(self):
        self._login(self.requester)
        self.client.post(reverse("finance:request_create"), {
            "amount": "100.00", "currency": "USD", "category": "travel", "reason": "Field visit fuel",
        })
        fin_request = FinancialRequest.objects.get()
        self.assertEqual(fin_request.status, FinancialRequestStatus.SUBMITTED)

        self._login(self.finance)
        self.client.post(reverse("finance:forward_request", args=[fin_request.pk]), {"finance_notes": ""})
        fin_request.refresh_from_db()
        self.assertEqual(fin_request.status, FinancialRequestStatus.FORWARDED)

        self._login(self.super_admin)
        self.client.post(reverse("finance:super_admin_decide", args=[fin_request.pk]), {
            "decision": "approve", "notes": "Looks fine",
        })
        fin_request.refresh_from_db()
        self.assertEqual(fin_request.status, FinancialRequestStatus.APPROVED)

        self._login(self.finance)
        response = self.client.post(reverse("finance:confirm_disbursement", args=[fin_request.pk]), {
            "account_type": "cash",
        })
        fin_request.refresh_from_db()
        self.assertEqual(fin_request.status, FinancialRequestStatus.DISBURSED)
        self.assertEqual(response.status_code, 302)

        balance = FinanceBalance.get_solo()
        self.assertEqual(balance.cash_usd, Decimal("-100.00"))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_cannot_skip_straight_to_disbursement(self):
        """A request still SUBMITTED (never forwarded/approved) must not be disbursable."""
        fin_request = FinancialRequest.objects.create(
            requested_by=self.requester, amount=Decimal("50.00"), currency="USD",
            category="travel", reason="x", status=FinancialRequestStatus.SUBMITTED,
        )
        self._login(self.finance)
        response = self.client.post(reverse("finance:confirm_disbursement", args=[fin_request.pk]), {
            "account_type": "cash",
        })
        self.assertEqual(response.status_code, 404)
        fin_request.refresh_from_db()
        self.assertEqual(fin_request.status, FinancialRequestStatus.SUBMITTED)

    def test_declined_request_blocks_disbursement(self):
        fin_request = FinancialRequest.objects.create(
            requested_by=self.requester, amount=Decimal("50.00"), currency="USD",
            category="travel", reason="x", status=FinancialRequestStatus.DECLINED,
        )
        self._login(self.finance)
        response = self.client.post(reverse("finance:confirm_disbursement", args=[fin_request.pk]), {
            "account_type": "cash",
        })
        self.assertEqual(response.status_code, 404)


class FinancialRequestIDORTests(TestCase):
    """A requester must never be able to see or act on someone else's request."""

    def setUp(self):
        self.alice = make_user("alice", "media")
        self.bob = make_user("bob", "media")
        self.fin_request = FinancialRequest.objects.create(
            requested_by=self.alice, amount=Decimal("30.00"), currency="USD",
            category="travel", reason="Alice's request", status=FinancialRequestStatus.INFO_REQUESTED,
        )

    def test_my_requests_only_shows_own_requests(self):
        self.client.force_login(self.bob)
        response = self.client.get(reverse("finance:my_requests"))
        self.assertNotContains(response, "Alice's request")

    def test_cannot_submit_additional_info_on_someone_elses_request(self):
        self.client.force_login(self.bob)
        response = self.client.post(
            reverse("finance:submit_additional_info", args=[self.fin_request.pk]),
            {"additional_info": "trying to tamper"},
        )
        self.assertEqual(response.status_code, 404)
        self.fin_request.refresh_from_db()
        self.assertEqual(self.fin_request.additional_info, "")


class ProgramManagerCanRequestFundsTests(TestCase):
    def test_program_manager_can_submit_a_financial_request(self):
        pm = make_user("pm1", "program_manager")
        self.client.force_login(pm)
        response = self.client.post(reverse("finance:request_create"), {
            "amount": "40.00", "currency": "USD", "category": "travel", "reason": "Site visit",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialRequest.objects.filter(requested_by=pm).count(), 1)

    def test_program_manager_can_view_their_own_requests(self):
        pm = make_user("pm1", "program_manager")
        self.client.force_login(pm)
        response = self.client.get(reverse("finance:my_requests"))
        self.assertEqual(response.status_code, 200)


class FinanceRoleAccessTests(TestCase):
    def test_program_manager_cannot_reach_finance_queue(self):
        self.client.force_login(make_user("pm2", "program_manager"))
        response = self.client.get(reverse("finance:request_queue"))
        self.assertEqual(response.status_code, 403)

    def test_program_manager_cannot_reach_super_admin_queue(self):
        self.client.force_login(make_user("pm3", "program_manager"))
        response = self.client.get(reverse("finance:super_admin_queue"))
        self.assertEqual(response.status_code, 403)
