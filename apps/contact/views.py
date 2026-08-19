from django.shortcuts import render, redirect
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import ContactInfo
from .forms import ContactInfoForm


def public_contact(request):
    info = ContactInfo.get_solo()
    return render(request, "contact/public_contact.html", {"info": info})


@role_required("super_admin")
def manage_contact(request):
    info = ContactInfo.get_solo()
    if request.method == "POST":
        form = ContactInfoForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated contact information")
            messages.success(request, "Contact information updated.")
            return redirect("contact:manage_contact")
    else:
        form = ContactInfoForm(instance=info)
    return render(request, "contact/manage_contact.html", {"form": form})