from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from apps.core.captcha import verify_turnstile
from .models import Donation, DonationSettings, DonationStatus
from .forms import DonationForm, DonationProofForm, DonationSettingsForm


@ratelimit(key="ip", rate="5/h", method="POST")
def donate(request):
    if request.method == "POST":
        form = DonationForm(request.POST)
        if getattr(request, "limited", False):
            messages.error(request, "Too many submissions from this connection — please try again later.")
        elif not verify_turnstile(request):
            messages.error(request, "Verification failed — please try again.")
        elif form.is_valid():
            if form.cleaned_data.get("website"):
                return redirect("donations:donate")  # honeypot tripped — drop it silently
            donation = form.save()
            return redirect("donations:donate_thanks", reference_code=donation.reference_code)
    else:
        form = DonationForm(initial={"amount": 25})
    return render(request, "donations/donate.html", {"form": form})


@ratelimit(key="ip", rate="10/h", method="POST")
def donate_thanks(request, reference_code):
    donation = get_object_or_404(Donation, reference_code=reference_code)
    settings_obj = DonationSettings.get_solo()
    proof_form = None
    if donation.status in (DonationStatus.PENDING, DonationStatus.REJECTED):
        if request.method == "POST":
            if getattr(request, "limited", False):
                messages.error(request, "Too many attempts from this connection — please try again later.")
                proof_form = DonationProofForm(instance=donation)
            else:
                proof_form = DonationProofForm(request.POST, request.FILES, instance=donation)
                if proof_form.is_valid():
                    proof = proof_form.save(commit=False)
                    proof.proof_uploaded_at = timezone.now()
                    proof.status = DonationStatus.PENDING
                    proof.save()
                    messages.success(request, "Proof of payment uploaded — our finance team will review it shortly.")
                    return redirect("donations:donate_thanks", reference_code=reference_code)
        else:
            proof_form = DonationProofForm(instance=donation)
    return render(request, "donations/donate_thanks.html", {
        "donation": donation, "settings": settings_obj, "proof_form": proof_form,
    })


@role_required("finance")
def donation_list(request):
    donations = Donation.objects.all()
    return render(request, "donations/donation_list.html", {"donations": donations})


@role_required("finance")
@transaction.atomic
def donation_confirm(request, pk):
    donation = get_object_or_404(Donation, pk=pk, status=DonationStatus.PENDING)
    if request.method == "POST":
        if "reject" in request.POST:
            donation.status = DonationStatus.REJECTED
            donation.save()
            log_action(request.user, "Rejected donation proof", donation.reference_code)
            messages.success(request, "Donation rejected. The donor can resubmit proof of payment.")
            return redirect("donations:donation_list")

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


@role_required("finance")
def donation_proof_download(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    if not donation.proof_of_payment:
        raise Http404
    return FileResponse(
        donation.proof_of_payment.open("rb"),
        filename=donation.proof_of_payment.name.rsplit("/", 1)[-1],
    )


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