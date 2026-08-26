from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django_ratelimit.decorators import ratelimit
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from apps.core.captcha import verify_turnstile
from .models import ContactInfo, NewsletterSubscriber
from .forms import ContactInfoForm, NewsletterSubscriberForm


def public_contact(request):
    info = ContactInfo.get_solo()
    return render(request, "contact/public_contact.html", {"info": info})


def _safe_next(request, fallback):
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return next_url
    return fallback


@ratelimit(key="ip", rate="10/h", method="POST")
def newsletter_signup(request):
    fallback = reverse("newsfeed:landing")
    if request.method != "POST":
        return redirect(fallback)

    next_url = _safe_next(request, fallback)
    if getattr(request, "limited", False):
        messages.error(request, "Too many submissions from this connection — please try again later.")
        return redirect(next_url)
    if not verify_turnstile(request):
        messages.error(request, "Verification failed — please try again.")
        return redirect(next_url)

    form = NewsletterSubscriberForm(request.POST)
    if form.is_valid():
        if form.cleaned_data.get("website"):
            return redirect(next_url)  # honeypot tripped — drop it silently
        _, created = NewsletterSubscriber.objects.get_or_create(email=form.cleaned_data["email"])
        if created:
            messages.success(request, "You're subscribed! Thanks for staying connected.")
        else:
            messages.success(request, "You're already on the list — thanks for staying connected.")
    else:
        messages.error(request, "Please enter a valid email address.")
    return redirect(next_url)


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