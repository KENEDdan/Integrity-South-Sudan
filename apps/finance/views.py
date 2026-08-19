from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from apps.notifications.utils import notify, notify_role
from .models import FinanceBalance, Transaction, FinancialRequest, FinancialRequestStatus
from .forms import (
    FinancialRequestForm, ForwardRequestForm, SuperAdminDecisionForm,
    AdditionalInfoForm, DisbursementForm, TransactionForm,
)


@role_required("finance", "hr", "media", "program_manager", "super_admin")
def request_create(request):
    if request.method == "POST":
        form = FinancialRequestForm(request.POST)
        if form.is_valid():
            fin_request = form.save(commit=False)
            fin_request.requested_by = request.user
            fin_request.save()
            notify_role(
                "finance",
                f"New financial request from {request.user.get_full_name() or request.user.username}",
                sender=request.user, link="/finance/queue/", related_object=fin_request,
            )
            log_action(request.user, "Submitted financial request", f"{fin_request.currency} {fin_request.amount}")
            messages.success(request, "Your financial request has been submitted to Finance.")
            return redirect("finance:my_requests")
    else:
        form = FinancialRequestForm()
    return render(request, "finance/request_form.html", {"form": form})


@role_required("finance", "hr", "media", "program_manager", "super_admin")
def my_requests(request):
    requests_qs = FinancialRequest.objects.filter(requested_by=request.user)
    return render(request, "finance/my_requests.html", {"requests": requests_qs})


@role_required("finance")
def finance_request_queue(request):
    pending = FinancialRequest.objects.filter(status=FinancialRequestStatus.SUBMITTED)
    approved_awaiting = FinancialRequest.objects.filter(status=FinancialRequestStatus.APPROVED)
    declined_awaiting = FinancialRequest.objects.filter(
        status=FinancialRequestStatus.DECLINED, executed_by_finance__isnull=True,
    )
    return render(request, "finance/request_queue.html", {
        "pending": pending, "approved_awaiting": approved_awaiting, "declined_awaiting": declined_awaiting,
    })


@role_required("finance")
def forward_request(request, pk):
    fin_request = get_object_or_404(FinancialRequest, pk=pk, status=FinancialRequestStatus.SUBMITTED)
    if request.method == "POST":
        form = ForwardRequestForm(request.POST)
        if form.is_valid():
            fin_request.finance_notes = form.cleaned_data["finance_notes"]
            fin_request.status = FinancialRequestStatus.FORWARDED
            fin_request.reviewed_by_finance = request.user
            fin_request.save()
            notify_role(
                "super_admin", f"Financial request #{fin_request.pk} forwarded for your approval",
                sender=request.user, link="/finance/super-admin-queue/", related_object=fin_request,
            )
            log_action(request.user, "Forwarded financial request", f"Request #{fin_request.pk}")
            messages.success(request, "Request forwarded to Super Admin.")
            return redirect("finance:request_queue")
    else:
        form = ForwardRequestForm()
    return render(request, "finance/forward_request.html", {"form": form, "fin_request": fin_request})


@role_required("super_admin")
def super_admin_queue(request):
    pending = FinancialRequest.objects.filter(status=FinancialRequestStatus.FORWARDED)
    return render(request, "finance/super_admin_queue.html", {"pending": pending})


@role_required("super_admin")
def super_admin_decide(request, pk):
    fin_request = get_object_or_404(FinancialRequest, pk=pk, status=FinancialRequestStatus.FORWARDED)
    if request.method == "POST":
        form = SuperAdminDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            fin_request.super_admin_notes = form.cleaned_data["notes"]
            fin_request.decided_by_super_admin = request.user

            if decision == "approve":
                fin_request.status = FinancialRequestStatus.APPROVED
                notify(fin_request.requested_by, f"Your financial request #{fin_request.pk} was approved", sender=request.user)
                notify_role("finance", f"Request #{fin_request.pk} approved — ready to disburse", sender=request.user)
            elif decision == "info":
                fin_request.status = FinancialRequestStatus.INFO_REQUESTED
                notify(fin_request.requested_by, f"More information needed for request #{fin_request.pk}", sender=request.user)
            else:
                fin_request.status = FinancialRequestStatus.DECLINED
                notify(fin_request.requested_by, f"Your financial request #{fin_request.pk} was declined", sender=request.user)
                notify_role("finance", f"Request #{fin_request.pk} was declined by Super Admin", sender=request.user)

            fin_request.save()
            log_action(request.user, f"Decided on financial request ({decision})", f"Request #{fin_request.pk}")
            messages.success(request, "Decision recorded.")
            return redirect("finance:super_admin_queue")
    else:
        form = SuperAdminDecisionForm()
    return render(request, "finance/super_admin_decide.html", {"form": form, "fin_request": fin_request})


@role_required("finance", "hr", "media", "program_manager", "super_admin")
def submit_additional_info(request, pk):
    fin_request = get_object_or_404(
        FinancialRequest, pk=pk, requested_by=request.user, status=FinancialRequestStatus.INFO_REQUESTED,
    )
    if request.method == "POST":
        form = AdditionalInfoForm(request.POST)
        if form.is_valid():
            fin_request.additional_info = form.cleaned_data["additional_info"]
            fin_request.status = FinancialRequestStatus.FORWARDED
            fin_request.save()
            notify_role("super_admin", f"Additional info supplied for request #{fin_request.pk}", sender=request.user)
            messages.success(request, "Additional information submitted to Super Admin.")
            return redirect("finance:my_requests")
    else:
        form = AdditionalInfoForm()
    return render(request, "finance/additional_info_form.html", {"form": form, "fin_request": fin_request})


@role_required("finance")
@transaction.atomic
def confirm_disbursement(request, pk):
    fin_request = get_object_or_404(FinancialRequest, pk=pk, status=FinancialRequestStatus.APPROVED)
    if request.method == "POST":
        form = DisbursementForm(request.POST)
        if form.is_valid():
            Transaction.objects.create(
                transaction_type="expense",
                account_type=form.cleaned_data["account_type"],
                currency=fin_request.currency,
                amount=fin_request.amount,
                expense_category=fin_request.category,
                description=f"Disbursement for request #{fin_request.pk}: {fin_request.reason}",
                date=timezone.now().date(),
                recorded_by=request.user,
                related_request=fin_request,
            )
            fin_request.status = FinancialRequestStatus.DISBURSED
            fin_request.executed_by_finance = request.user
            fin_request.save()
            notify(fin_request.requested_by, f"Your financial request #{fin_request.pk} has been disbursed", sender=request.user)
            log_action(request.user, "Disbursed financial request", f"Request #{fin_request.pk}")
            messages.success(request, "Disbursement recorded and balances updated.")
            return redirect("finance:request_queue")
    else:
        form = DisbursementForm()
    return render(request, "finance/confirm_disbursement.html", {"form": form, "fin_request": fin_request})


@role_required("finance")
def acknowledge_decline(request, pk):
    fin_request = get_object_or_404(
        FinancialRequest, pk=pk, status=FinancialRequestStatus.DECLINED, executed_by_finance__isnull=True,
    )
    if request.method == "POST":
        fin_request.executed_by_finance = request.user
        fin_request.save()
        log_action(request.user, "Acknowledged declined financial request", f"Request #{fin_request.pk}")
        messages.success(request, "Decline acknowledged and finalized.")
        return redirect("finance:request_queue")
    return render(request, "finance/acknowledge_decline.html", {"fin_request": fin_request})


@role_required("finance")
@transaction.atomic
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.recorded_by = request.user
            transaction.save()
            log_action(request.user, f"Recorded {transaction.transaction_type}", f"{transaction.currency} {transaction.amount}")
            messages.success(request, "Transaction recorded and balances updated.")
            return redirect("finance:dashboard_balances")
    else:
        form = TransactionForm()
    return render(request, "finance/transaction_form.html", {"form": form})


@role_required("finance", "super_admin")
def dashboard_balances(request):
    balance = FinanceBalance.get_solo()
    recent_transactions = Transaction.objects.all()[:15]
    return render(request, "finance/balances.html", {"balance": balance, "transactions": recent_transactions})