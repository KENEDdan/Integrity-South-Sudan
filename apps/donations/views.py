from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import Donation, DonationSettings, DonationStatus
from .forms import DonationForm, DonationSettingsForm


def donate(request):
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("website"):
                return redirect("donations:donate")  # honeypot tripped — drop it silently
            donation = form.save()
            return redirect("donations:donate_thanks", pk=donation.pk)
    else:
        form = DonationForm(initial={"amount": 25})
    return render(request, "donations/donate.html", {"form": form})


def donate_thanks(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    settings_obj = DonationSettings.get_solo()
    return render(request, "donations/donate_thanks.html", {"donation": donation, "settings": settings_obj})


@role_required("finance")
def donation_list(request):
    donations = Donation.objects.all()
    return render(request, "donations/donation_list.html", {"donations": donations})


@role_required("finance")
@transaction.atomic
def donation_confirm(request, pk):
    donation = get_object_or_404(Donation, pk=pk, status=DonationStatus.PENDING)
    if request.method == "POST":
        from apps.finance.models import Transaction
        Transaction.objects.create(
            transaction_type="income",
            account_type="bank",
            currency=donation.currency,
            amount=donation.amount,
            income_source="donor",
            description=f"Donation from {donation.donor_name} (ref {donation.reference_code})",
            date=timezone.now().date(),
            recorded_by=request.user,
        )
        donation.status = DonationStatus.CONFIRMED
        donation.confirmed_by = request.user
        donation.confirmed_at = timezone.now()
        donation.save()
        log_action(request.user, "Confirmed donation", f"{donation.reference_code}: {donation.currency} {donation.amount}")
        messages.success(request, "Donation confirmed and recorded in Finance.")
        return redirect("donations:donation_list")
    return render(request, "donations/donation_confirm.html", {"donation": donation})


@role_required("super_admin")
def donation_settings(request):
    settings_obj = DonationSettings.get_solo()
    if request.method == "POST":
        form = DonationSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated donation bank details")
            messages.success(request, "Donation settings updated.")
            return redirect("donations:donation_settings")
    else:
        form = DonationSettingsForm(instance=settings_obj)
    return render(request, "donations/donation_settings.html", {"form": form})