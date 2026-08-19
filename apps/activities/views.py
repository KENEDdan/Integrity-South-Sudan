from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import Activity, ActivityType
from .forms import ActivityForm, ActivityMediaFormSet


def public_list(request):
    activity_type = request.GET.get("type", "")
    activities = Activity.objects.filter(is_published=True)
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    return render(request, "activities/public_list.html", {
        "activities": activities, "types": ActivityType.choices, "active_type": activity_type,
    })


def public_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk, is_published=True)
    return render(request, "activities/public_detail.html", {"activity": activity})


@role_required("media")
def manage_list(request):
    activities = Activity.objects.all()
    return render(request, "activities/manage_list.html", {"activities": activities})


@role_required("media")
def activity_create(request):
    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            formset = ActivityMediaFormSet(request.POST, request.FILES, instance=activity)
            if formset.is_valid():
                formset.save()
            log_action(request.user, "Added activity", activity.title)
            messages.success(request, f'"{activity.title}" was added.')
            return redirect("activities:manage_list")
    else:
        form = ActivityForm()
        formset = ActivityMediaFormSet()
    return render(request, "activities/activity_form.html", {"form": form, "formset": formset, "mode": "Add"})


@role_required("media")
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES, instance=activity)
        formset = ActivityMediaFormSet(request.POST, request.FILES, instance=activity)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            log_action(request.user, "Updated activity", activity.title)
            messages.success(request, f'"{activity.title}" was updated.')
            return redirect("activities:manage_list")
    else:
        form = ActivityForm(instance=activity)
        formset = ActivityMediaFormSet(instance=activity)
    return render(request, "activities/activity_form.html", {
        "form": form, "formset": formset, "mode": "Edit", "activity": activity,
    })


@role_required("media")
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        title = activity.title
        activity.delete()
        log_action(request.user, "Deleted activity", title)
        messages.success(request, f'"{title}" was deleted.')
        return redirect("activities:manage_list")
    return render(request, "activities/activity_confirm_delete.html", {"activity": activity})