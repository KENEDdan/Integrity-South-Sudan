from django.shortcuts import render
from apps.accounts.decorators import role_required
from .models import AuditLogEntry


@role_required("super_admin")
def log_list(request):
    entries = AuditLogEntry.objects.all()[:200]
    return render(request, "audit/log_list.html", {"entries": entries})