from django.shortcuts import render, redirect
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import AboutUs
from .forms import AboutUsForm


def public_about(request):
    info = AboutUs.get_solo()
    return render(request, "about/public_about.html", {"info": info})


@role_required("super_admin")
def manage_about(request):
    info = AboutUs.get_solo()
    if request.method == "POST":
        form = AboutUsForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated About Us content")
            messages.success(request, "About Us content updated.")
            return redirect("about:manage_about")
    else:
        form = AboutUsForm(instance=info)
    return render(request, "about/manage_about.html", {"form": form})