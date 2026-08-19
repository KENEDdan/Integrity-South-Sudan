from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Currency(models.TextChoices):
    USD = "USD", "US Dollar"
    SSP = "SSP", "South Sudanese Pound"


class AccountType(models.TextChoices):
    CASH = "cash", "Cash at Hand"
    BANK = "bank", "In Bank"


class TransactionType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class IncomeSource(models.TextChoices):
    DONOR = "donor", "Donor Contribution"
    GRANT = "grant", "Grant"
    PARTNER = "partner", "Partner Funding"
    MEMBERSHIP = "membership", "Membership Fees"
    OTHER = "other", "Other"


class ExpenseCategory(models.TextChoices):
    CAPACITY_BUILDING = "capacity_building", "Capacity Building"
    RADIO_PROGRAMS = "radio_programs", "Radio Programs"
    SCHOOL_CLUBS = "school_clubs", "School Clubs"
    COMMUNITY_DIALOGUE = "community_dialogue", "Community Dialogue"
    CIVIC_EDUCATION = "civic_education", "Civic Education"
    OPERATIONAL = "operational", "Operational"
    TRAVEL = "travel", "Travel & Transport"
    PROCUREMENT = "procurement", "Procurement"
    OTHER = "other", "Other"


class FinanceBalance(models.Model):
    """Singleton row holding running totals for all four buckets."""
    cash_usd = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    cash_ssp = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    bank_usd = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    bank_ssp = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def apply(self, account_type, currency, delta):
        """Atomic DB-level increment (UPDATE ... SET x = x + delta) so concurrent
        transactions can never silently clobber each other's balance update."""
        field = f"{account_type}_{currency.lower()}"
        type(self).objects.filter(pk=self.pk).update(**{field: F(field) + delta}, updated_at=timezone.now())
        self.refresh_from_db(fields=[field, "updated_at"])

    def __str__(self):
        return "Organization Finance Balance"


class Transaction(models.Model):
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    account_type = models.CharField(max_length=10, choices=AccountType.choices)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    income_source = models.CharField(max_length=20, choices=IncomeSource.choices, blank=True)
    expense_category = models.CharField(max_length=30, choices=ExpenseCategory.choices, blank=True)
    description = models.TextField()
    date = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transactions_recorded",
    )
    related_request = models.ForeignKey(
        "FinancialRequest", null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions",
    )
    related_project = models.ForeignKey(
        "projects.Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="expense_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def clean(self):
        if self.transaction_type == TransactionType.INCOME and not self.income_source:
            raise ValidationError({"income_source": "Required for income entries."})
        if self.transaction_type == TransactionType.EXPENSE and not self.expense_category:
            raise ValidationError({"expense_category": "Required for expense entries."})

    def __str__(self):
        return f"{self.get_transaction_type_display()} — {self.currency} {self.amount}"


@receiver(post_save, sender=Transaction)
def update_balance_on_transaction(sender, instance, created, **kwargs):
    if not created:
        return
    balance = FinanceBalance.get_solo()
    delta = instance.amount if instance.transaction_type == TransactionType.INCOME else -instance.amount
    balance.apply(instance.account_type, instance.currency, delta)


class FinancialRequestStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted — Awaiting Finance Review"
    FORWARDED = "forwarded", "Forwarded to Super Admin"
    INFO_REQUESTED = "info_requested", "More Information Requested"
    APPROVED = "approved", "Approved — Awaiting Disbursement"
    DECLINED = "declined", "Declined"
    DISBURSED = "disbursed", "Disbursed"


class FinancialRequest(models.Model):
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="financial_requests",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    category = models.CharField(max_length=30, choices=ExpenseCategory.choices)
    reason = models.TextField(help_text="Explain clearly why this money is needed.")
    status = models.CharField(
        max_length=20, choices=FinancialRequestStatus.choices, default=FinancialRequestStatus.SUBMITTED,
    )

    finance_notes = models.TextField(blank=True)
    super_admin_notes = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)

    reviewed_by_finance = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests_forwarded",
    )
    decided_by_super_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests_decided",
    )
    executed_by_finance = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests_executed",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Request #{self.pk} — {self.currency} {self.amount} ({self.get_status_display()})"