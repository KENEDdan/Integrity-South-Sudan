import logging
import secrets
import string

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from .decorators import role_required
from apps.audit.utils import log_action
from .forms import StyledPasswordChangeForm, AdminAccountForm
from .models import User

logger = logging.getLogger(__name__)

DASHBOARD_TEMPLATES = {
    "super_admin": "accounts/dashboards/super_admin.html",
    "hr": "accounts/dashboards/hr.html",
    "finance": "accounts/dashboards/finance.html",
    "media": "accounts/dashboards/media.html",
    "program_manager": "accounts/dashboards/program_manager.html",
}


@login_required
def dashboard(request):
    user = request.user
    template_name = DASHBOARD_TEMPLATES.get(user.role, "accounts/dashboard_base.html")
    context = {"user": user}

    if user.role in ("super_admin", "finance"):
        from apps.finance.models import FinanceBalance
        context["balance"] = FinanceBalance.get_solo()

    if user.role in ("super_admin", "program_manager"):
        from apps.projects.models import Project, Issue, FieldReport
        context["project_count"] = Project.objects.count()
        context["open_issue_count"] = Issue.objects.filter(status="open").count()
        context["pending_report_count"] = FieldReport.objects.filter(status="pending").count()

    return render(request, template_name, context)


class ForcedPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=["must_change_password"])
        messages.success(self.request, "Password updated successfully.")
        return response


def _generate_temp_password():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12))


def _send_temp_password_email(request, account, temp_password, is_reset=False):
    """Emails the temp password to the account's own address (the one entered
    when it was created). Returns True/False rather than raising, so a mail
    failure never blocks account creation/reset — just falls back to the
    on-screen password the super_admin can relay manually."""
    if not account.email:
        return False
    login_url = request.build_absolute_uri(reverse("accounts:login"))
    if is_reset:
        subject = "Your Integrity South Sudan password was reset"
        intro = "Your password on the Integrity South Sudan system has been reset."
    else:
        subject = "Your Integrity South Sudan account"
        intro = "An account has been created for you on the Integrity South Sudan system."
    message = (
        f"Hello {account.get_full_name() or account.username},\n\n"
        f"{intro}\n\n"
        f"Username: {account.username}\n"
        f"Temporary password: {temp_password}\n\n"
        f"Log in here: {login_url}\n"
        "You'll be required to set a new password the first time you log in.\n\n"
        "If you weren't expecting this, please contact your administrator."
    )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [account.email], fail_silently=False)
        return True
    except Exception:
        logger.exception("Failed to send account email to %s", account.email)
        return False


@role_required("super_admin")
def admin_account_list(request):
    accounts = User.objects.all().order_by("role", "username")
    return render(request, "accounts/admin_account_list.html", {"accounts": accounts})


@role_required("super_admin")
def admin_account_create(request):
    if request.method == "POST":
        form = AdminAccountForm(request.POST)
        if form.is_valid():
            temp_password = _generate_temp_password()
            account = form.save(commit=False)
            account.set_password(temp_password)
            account.must_change_password = True
            account.created_by = request.user
            account.save()
            log_action(request.user, "Created admin account", f"{account.username} ({account.role})")
            email_sent = _send_temp_password_email(request, account, temp_password)
            if account.email and not email_sent:
                messages.error(request, "Account created, but the notification email failed to send — share the temporary password with them directly.")
            return render(request, "accounts/admin_account_created.html", {
                "account": account, "temp_password": temp_password, "email_sent": email_sent,
            })
    else:
        form = AdminAccountForm()
    return render(request, "accounts/admin_account_form.html", {"form": form, "mode": "Add"})


@role_required("super_admin")
def admin_account_toggle_active(request, pk):
    account = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if account == request.user:
            messages.error(request, "You can't deactivate your own account.")
            return redirect("accounts:admin_account_list")
        account.is_active = not account.is_active
        account.save(update_fields=["is_active"])
        log_action(
            request.user, "Toggled account active status",
            f"{account.username}: now {'active' if account.is_active else 'inactive'}",
        )
        messages.success(request, f"{account.username} is now {'active' if account.is_active else 'inactive'}.")
    return redirect("accounts:admin_account_list")


@role_required("super_admin")
def admin_account_reset_password(request, pk):
    account = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        temp_password = _generate_temp_password()
        account.set_password(temp_password)
        account.must_change_password = True
        account.save()
        log_action(request.user, "Reset admin password", account.username)
        email_sent = _send_temp_password_email(request, account, temp_password, is_reset=True)
        if account.email and not email_sent:
            messages.error(request, "Password reset, but the notification email failed to send — share the temporary password with them directly.")
        return render(request, "accounts/admin_account_created.html", {
            "account": account, "temp_password": temp_password, "is_reset": True, "email_sent": email_sent,
        })
    return render(request, "accounts/admin_account_confirm_reset.html", {"account": account})