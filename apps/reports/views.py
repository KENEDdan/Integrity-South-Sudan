from datetime import timedelta
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.accounts.decorators import role_required
from apps.projects.models import (
    Project, ProjectStatus, ProjectTask, TaskStatus, FieldReport, FieldReportStatus, BeneficiaryRecord,
)
from apps.finance.models import FinanceBalance, Transaction, TransactionType, Currency
from apps.hr.models import Staff, StaffStatus


@role_required("super_admin")
def org_overview(request):
    today = timezone.now().date()
    year_start = today.replace(month=1, day=1)

    projects = Project.objects.all()
    active_projects = projects.filter(status=ProjectStatus.ACTIVE)

    budget_rows = []
    for currency, _ in Currency.choices:
        currency_projects = projects.filter(budget_currency=currency)
        budget = currency_projects.aggregate(total=Sum("budget_amount"))["total"] or 0
        spent = sum(p.spent_amount for p in currency_projects)
        percent = round((spent / budget) * 100, 1) if budget else 0
        budget_rows.append({
            "currency": currency, "budget": budget, "spent": spent,
            "remaining": budget - spent, "percent": percent,
        })

    beneficiaries_ytd = BeneficiaryRecord.objects.filter(
        period_date__gte=year_start
    ).aggregate(total=Sum("actual_count"))["total"] or 0

    finance_rows = []
    for currency, _ in Currency.choices:
        income = Transaction.objects.filter(
            transaction_type=TransactionType.INCOME, currency=currency
        ).aggregate(total=Sum("amount"))["total"] or 0
        expense = Transaction.objects.filter(
            transaction_type=TransactionType.EXPENSE, currency=currency
        ).aggregate(total=Sum("amount"))["total"] or 0
        finance_rows.append({"currency": currency, "income": income, "expense": expense, "net": income - expense})

    balance = FinanceBalance.get_solo()

    overdue_field_reports = FieldReport.objects.filter(
        status=FieldReportStatus.PENDING, report_date__lte=today - timedelta(days=7)
    )
    projects_ending_soon = projects.filter(
        end_date__isnull=False, end_date__gte=today, end_date__lte=today + timedelta(days=60)
    ).exclude(status=ProjectStatus.COMPLETED)
    overdue_tasks = ProjectTask.objects.exclude(status=TaskStatus.COMPLETED).filter(
        due_date__isnull=False, due_date__lt=today
    )

    manager_breakdown = (
        projects.exclude(program_manager__isnull=True)
        .values("program_manager__first_name", "program_manager__last_name", "program_manager__username")
        .annotate(
            total=Count("id"),
            active=Count("id", filter=Q(status=ProjectStatus.ACTIVE)),
            completed=Count("id", filter=Q(status=ProjectStatus.COMPLETED)),
        )
    )

    active_staff_count = Staff.objects.filter(status=StaffStatus.ACTIVE).count()

    context = {
        "active_projects_count": active_projects.count(),
        "total_projects_count": projects.count(),
        "budget_rows": budget_rows,
        "beneficiaries_ytd": beneficiaries_ytd,
        "finance_rows": finance_rows,
        "balance": balance,
        "overdue_field_reports": overdue_field_reports,
        "projects_ending_soon": projects_ending_soon,
        "overdue_tasks": overdue_tasks,
        "manager_breakdown": manager_breakdown,
        "active_staff_count": active_staff_count,
    }
    return render(request, "reports/org_overview.html", context)