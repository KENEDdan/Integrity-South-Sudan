from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import Achievement
from .forms import AchievementForm, AchievementMediaFormSet


def public_list(request):
    achievements = Achievement.objects.filter(is_published=True)
    return render(request, "achievements/public_list.html", {"achievements": achievements})


def public_detail(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, is_published=True)
    return render(request, "achievements/public_detail.html", {"achievement": achievement})


@role_required("media")
def manage_list(request):
    achievements = Achievement.objects.all()
    return render(request, "achievements/manage_list.html", {"achievements": achievements})


@role_required("media")
def achievement_create(request):
    if request.method == "POST":
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.created_by = request.user
            achievement.save()
            formset = AchievementMediaFormSet(request.POST, request.FILES, instance=achievement)
            if formset.is_valid():
                formset.save()
            log_action(request.user, "Added achievement", achievement.title)
            messages.success(request, f'"{achievement.title}" was added.')
            return redirect("achievements:manage_list")
    else:
        form = AchievementForm()
        formset = AchievementMediaFormSet()
    return render(request, "achievements/achievement_form.html", {"form": form, "formset": formset, "mode": "Add"})


@role_required("media")
def achievement_edit(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk)
    if request.method == "POST":
        form = AchievementForm(request.POST, request.FILES, instance=achievement)
        formset = AchievementMediaFormSet(request.POST, request.FILES, instance=achievement)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            log_action(request.user, "Updated achievement", achievement.title)
            messages.success(request, f'"{achievement.title}" was updated.')
            return redirect("achievements:manage_list")
    else:
        form = AchievementForm(instance=achievement)
        formset = AchievementMediaFormSet(instance=achievement)
    return render(request, "achievements/achievement_form.html", {
        "form": form, "formset": formset, "mode": "Edit", "achievement": achievement,
    })


@role_required("media")
def achievement_delete(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk)
    if request.method == "POST":
        title = achievement.title
        achievement.delete()
        log_action(request.user, "Deleted achievement", title)
        messages.success(request, f'"{title}" was deleted.')
        return redirect("achievements:manage_list")
    return render(request, "achievements/achievement_confirm_delete.html", {"achievement": achievement})