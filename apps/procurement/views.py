from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from apps.notifications.utils import notify_role
from .models import Requisition, RequisitionStatus, PurchaseOrder
from .forms import VendorForm, RequisitionForm, RequisitionDecisionForm, PurchaseOrderForm, DeliveryForm


@role_required("finance", "hr", "media", "program_manager")
def requisition_create(request):
    if request.method == "POST":
        form = RequisitionForm(request.POST)
        if form.is_valid():
            requisition = form.save(commit=False)
            requisition.requested_by = request.user
            requisition.save()
            notify_role(
                "finance", f"New procurement requisition from {request.user.get_full_name() or request.user.username}",
                sender=request.user, link="/procurement/requisitions/",
            )
            messages.success(request, "Requisition submitted.")
            return redirect("procurement:my_requisitions")
    else:
        form = RequisitionForm()
    return render(request, "procurement/simple_form.html", {"form": form, "title": "New Requisition"})


@role_required("finance", "hr", "media", "program_manager")
def my_requisitions(request):
    requisitions = Requisition.objects.filter(requested_by=request.user)
    return render(request, "procurement/my_requisitions.html", {"requisitions": requisitions})


@role_required("finance")
def requisition_queue(request):
    pending = Requisition.objects.filter(status=RequisitionStatus.PENDING)
    approved = Requisition.objects.filter(status=RequisitionStatus.APPROVED)
    return render(request, "procurement/requisition_queue.html", {"pending": pending, "approved": approved})


@role_required("finance")
def requisition_decide(request, pk):
    requisition = get_object_or_404(Requisition, pk=pk, status=RequisitionStatus.PENDING)
    if request.method == "POST":
        form = RequisitionDecisionForm(request.POST)
        if form.is_valid():
            requisition.status = (
                RequisitionStatus.APPROVED if form.cleaned_data["decision"] == "approve" else RequisitionStatus.DECLINED
            )
            requisition.decision_notes = form.cleaned_data["decision_notes"]
            requisition.decided_by = request.user
            requisition.save()
            log_action(request.user, f"Decided requisition ({form.cleaned_data['decision']})", f"Requisition #{requisition.pk}")
            messages.success(request, "Decision recorded.")
            return redirect("procurement:requisition_queue")
    else:
        form = RequisitionDecisionForm()
    return render(request, "procurement/simple_form.html", {"form": form, "title": f"Decide Requisition #{requisition.pk}"})


@role_required("finance")
def purchase_order_create(request, pk):
    requisition = get_object_or_404(Requisition, pk=pk, status=RequisitionStatus.APPROVED)
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save(commit=False)
            po.requisition = requisition
            po.po_number = f"PO-{timezone.now():%Y%m}-{requisition.pk:04d}"
            po.issued_by = request.user
            po.save()
            requisition.status = RequisitionStatus.CONVERTED
            requisition.save(update_fields=["status"])
            log_action(request.user, "Issued purchase order", po.po_number)
            messages.success(request, f"{po.po_number} issued.")
            return redirect("procurement:po_list")
    else:
        form = PurchaseOrderForm()
    return render(request, "procurement/simple_form.html", {"form": form, "title": f"Issue PO for Requisition #{requisition.pk}"})


@role_required("finance")
def po_list(request):
    orders = PurchaseOrder.objects.all()
    return render(request, "procurement/po_list.html", {"orders": orders})


@role_required("finance")
def delivery_record(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.purchase_order = po
            delivery.received_by = request.user
            delivery.save()
            po.status = "delivered"
            po.save(update_fields=["status"])
            log_action(request.user, "Recorded delivery", po.po_number)
            messages.success(request, "Delivery recorded.")
            return redirect("procurement:po_list")
    else:
        form = DeliveryForm()
    return render(request, "procurement/simple_form.html", {"form": form, "title": f"Record Delivery — {po.po_number}"})


@role_required("finance")
def vendor_list(request):
    from .models import Vendor
    vendors = Vendor.objects.all()
    return render(request, "procurement/vendor_list.html", {"vendors": vendors})


@role_required("finance")
def vendor_add(request):
    if request.method == "POST":
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor added.")
            return redirect("procurement:vendor_list")
    else:
        form = VendorForm()
    return render(request, "procurement/simple_form.html", {"form": form, "title": "Add Vendor"})