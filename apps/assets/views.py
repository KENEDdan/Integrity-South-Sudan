from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import Asset
from .forms import AssetForm, AssetLogForm


@role_required("finance")
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, "assets/asset_list.html", {"assets": assets})


@role_required("finance")
def asset_create(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.created_by = request.user
            asset.save()
            log_action(request.user, "Added asset", asset.name)
            messages.success(request, f'"{asset.name}" was added.')
            return redirect("assets:asset_detail", pk=asset.pk)
    else:
        form = AssetForm()
    return render(request, "assets/asset_form.html", {"form": form, "mode": "Add"})


@role_required("finance")
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, "assets/asset_detail.html", {"asset": asset})


@role_required("finance")
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated asset", asset.name)
            messages.success(request, f'"{asset.name}" was updated.')
            return redirect("assets:asset_detail", pk=asset.pk)
    else:
        form = AssetForm(instance=asset)
    return render(request, "assets/asset_form.html", {"form": form, "mode": "Edit", "asset": asset})


@role_required("finance")
def log_add(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.asset = asset
            log.recorded_by = request.user
            log.save()
            messages.success(request, "Log entry added.")
            return redirect("assets:asset_detail", pk=asset.pk)
    else:
        form = AssetLogForm()
    return render(request, "assets/simple_form.html", {"form": form, "title": f"Add Log — {asset.name}"})