import hmac
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.notifications.utils import notify_role
from .models import KoboSubmission


@csrf_exempt
@require_POST
def kobo_webhook(request):
    secret = request.headers.get("X-Webhook-Secret", "")
    expected_secret = getattr(settings, "KOBO_WEBHOOK_SECRET", None)
    if not secret or not expected_secret or not hmac.compare_digest(secret, expected_secret):
        return HttpResponseForbidden("Invalid or missing webhook secret.")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    form_uid = payload.get("_xform_id_string") or payload.get("formhub/uuid", "unknown")
    submission_id = str(payload.get("_id") or payload.get("_uuid") or "")

    if not submission_id:
        return JsonResponse({"error": "Missing submission id"}, status=400)

    submission, created = KoboSubmission.objects.get_or_create(
        form_uid=form_uid, submission_id=submission_id, defaults={"raw_data": payload},
    )
    if created:
        notify_role("program_manager", f"New KoboToolBox submission received ({form_uid})", link="/field-data/")

    return JsonResponse({"status": "ok", "created": created})


@role_required("program_manager")
def submission_list(request):
    submissions = KoboSubmission.objects.all()
    return render(request, "field_data/submission_list.html", {"submissions": submissions})


@role_required("program_manager")
def submission_detail(request, pk):
    submission = get_object_or_404(KoboSubmission, pk=pk)
    from apps.projects.models import Project
    if request.method == "POST":
        project_id = request.POST.get("related_project")
        submission.related_project = Project.objects.filter(pk=project_id).first() if project_id else None
        submission.status = "reviewed"
        submission.reviewed_by = request.user
        submission.save()
        messages.success(request, "Submission updated.")
        return redirect("field_data:submission_detail", pk=submission.pk)
    projects = Project.objects.all()
    return render(request, "field_data/submission_detail.html", {"submission": submission, "projects": projects})