from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from apps.core.captcha import verify_turnstile
from apps.notifications.utils import notify_role
from .models import Partner, PartnerRequest, PartnerRequestStatus
from .forms import PartnerForm, PartnerRequestForm, PartnerRequestDecisionForm


def public_list(request):
    partners = Partner.objects.filter(is_active=True)
    return render(request, "partners/public_list.html", {"partners": partners})


@ratelimit(key="ip", rate="5/h", method="POST")
def partner_request_create(request):
    if request.method == "POST":
        form = PartnerRequestForm(request.POST, request.FILES)
        if getattr(request, "limited", False):
            messages.error(request, "Too many submissions from this connection — please try again later.")
        elif not verify_turnstile(request):
            messages.error(request, "Verification failed — please try again.")
        elif form.is_valid():
            if form.cleaned_data.get("website"):
                return redirect("partners:public_list")  # honeypot tripped — drop it silently
            partner_request = form.save()
            notify_role(
                "super_admin", f"New partnership request from {partner_request.organization_name}",
                link="/partners/manage/requests/",
            )
            messages.success(request, "Your request has been submitted. We'll be in touch.")
            return redirect("partners:public_list")
    else:
        form = PartnerRequestForm()
    return render(request, "partners/request_form.html", {"form": form})


@role_required("super_admin")
def manage_list(request):
    partners = Partner.objects.all()
    return render(request, "partners/manage_list.html", {"partners": partners})


@role_required("super_admin")
def partner_create(request):
    if request.method == "POST":
        form = PartnerForm(request.POST, request.FILES)
        if form.is_valid():
            partner = form.save(commit=False)
            partner.created_by = request.user
            partner.save()
            log_action(request.user, "Added partner", partner.name)
            messages.success(request, f'"{partner.name}" was added.')
            return redirect("partners:manage_list")
    else:
        form = PartnerForm()
    return render(request, "partners/partner_form.html", {"form": form, "mode": "Add"})


@role_required("super_admin")
def partner_edit(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == "POST":
        form = PartnerForm(request.POST, request.FILES, instance=partner)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated partner", partner.name)
            messages.success(request, f'"{partner.name}" was updated.')
            return redirect("partners:manage_list")
    else:
        form = PartnerForm(instance=partner)
    return render(request, "partners/partner_form.html", {"form": form, "mode": "Edit", "partner": partner})


@role_required("super_admin")
def request_queue(request):
    pending = PartnerRequest.objects.filter(
        status__in=[PartnerRequestStatus.PENDING, PartnerRequestStatus.INFO_REQUESTED]
    )
    decided = PartnerRequest.objects.exclude(
        status__in=[PartnerRequestStatus.PENDING, PartnerRequestStatus.INFO_REQUESTED]
    )[:20]
    return render(request, "partners/request_queue.html", {"pending": pending, "decided": decided})


@role_required("super_admin")
def request_document_download(request, pk):
    partner_request = get_object_or_404(PartnerRequest, pk=pk)
    if not partner_request.registration_documents:
        raise Http404
    return FileResponse(
        partner_request.registration_documents.open("rb"),
        filename=partner_request.registration_documents.name.rsplit("/", 1)[-1],
    )


@role_required("super_admin")
def request_decide(request, pk):
    partner_request = get_object_or_404(PartnerRequest, pk=pk)
    if request.method == "POST":
        form = PartnerRequestDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            partner_request.admin_notes = form.cleaned_data["admin_notes"]
            partner_request.decided_by = request.user

            if decision == "approve":
                partner_request.status = PartnerRequestStatus.APPROVED
                Partner.objects.create(
                    name=partner_request.organization_name,
                    logo=partner_request.logo,
                    base_address=partner_request.address,
                    contact_address=partner_request.contact_email,
                    partnering_on=partner_request.reason[:255],
                    validity_note=partner_request.contract_validity,
                    created_by=request.user,
                )
            elif decision == "info":
                partner_request.status = PartnerRequestStatus.INFO_REQUESTED
            else:
                partner_request.status = PartnerRequestStatus.DECLINED

            partner_request.save()
            log_action(request.user, f"Decided partner request ({decision})", partner_request.organization_name)
            messages.success(request, "Decision recorded.")
            return redirect("partners:request_queue")
    else:
        form = PartnerRequestDecisionForm()
    return render(request, "partners/request_decide.html", {"form": form, "partner_request": partner_request})