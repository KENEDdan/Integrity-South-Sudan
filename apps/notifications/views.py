from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .forms import AnnouncementForm
from .utils import notify, notify_role



@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect(notification.link or "accounts:dashboard")


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect("accounts:dashboard")

    

@role_required("super_admin")
def send_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            target = form.cleaned_data["target"]
            message = form.cleaned_data["message"]
            if target == "all":
                from apps.accounts.models import User
                for recipient in User.objects.filter(is_active=True).exclude(pk=request.user.pk):
                    notify(recipient, message, sender=request.user)
            else:
                notify_role(target, message, sender=request.user)
            log_action(request.user, "Sent announcement", f"To: {target}")
            messages.success(request, "Announcement sent.")
            return redirect("accounts:dashboard")
    else:
        form = AnnouncementForm()
    return render(request, "notifications/announcement_form.html", {"form": form})