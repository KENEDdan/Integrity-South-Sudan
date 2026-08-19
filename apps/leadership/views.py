from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import Leader
from .forms import LeaderForm


def public_list(request):
    leaders = Leader.objects.filter(is_published=True)
    return render(request, "leadership/public_list.html", {"leaders": leaders})


def public_detail(request, pk):
    leader = get_object_or_404(Leader, pk=pk, is_published=True)
    return render(request, "leadership/public_detail.html", {"leader": leader})


@role_required("super_admin")
def manage_list(request):
    leaders = Leader.objects.all()
    return render(request, "leadership/manage_list.html", {"leaders": leaders})


@role_required("super_admin")
def leader_create(request):
    if request.method == "POST":
        form = LeaderForm(request.POST, request.FILES)
        if form.is_valid():
            leader = form.save(commit=False)
            leader.created_by = request.user
            leader.save()
            log_action(request.user, "Added leader profile", leader.name)
            messages.success(request, f'"{leader.name}" was added.')
            return redirect("leadership:manage_list")
    else:
        form = LeaderForm()
    return render(request, "leadership/leader_form.html", {"form": form, "mode": "Add"})


@role_required("super_admin")
def leader_edit(request, pk):
    leader = get_object_or_404(Leader, pk=pk)
    if request.method == "POST":
        form = LeaderForm(request.POST, request.FILES, instance=leader)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated leader profile", leader.name)
            messages.success(request, f'"{leader.name}" was updated.')
            return redirect("leadership:manage_list")
    else:
        form = LeaderForm(instance=leader)
    return render(request, "leadership/leader_form.html", {"form": form, "mode": "Edit", "leader": leader})