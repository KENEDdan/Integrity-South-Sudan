from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import Podcast
from .forms import PodcastForm


def public_list(request):
    podcasts = Podcast.objects.filter(is_published=True)
    return render(request, "podcasts/public_list.html", {"podcasts": podcasts})


def public_detail(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk, is_published=True)
    return render(request, "podcasts/public_detail.html", {"podcast": podcast})


@role_required("media")
def manage_list(request):
    podcasts = Podcast.objects.all()
    return render(request, "podcasts/manage_list.html", {"podcasts": podcasts})


@role_required("media")
def podcast_create(request):
    if request.method == "POST":
        form = PodcastForm(request.POST, request.FILES)
        if form.is_valid():
            podcast = form.save(commit=False)
            podcast.created_by = request.user
            podcast.save()
            log_action(request.user, "Added podcast", podcast.title)
            messages.success(request, f'"{podcast.title}" was added.')
            return redirect("podcasts:manage_list")
    else:
        form = PodcastForm()
    return render(request, "podcasts/podcast_form.html", {"form": form, "mode": "Add"})


@role_required("media")
def podcast_edit(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk)
    if request.method == "POST":
        form = PodcastForm(request.POST, request.FILES, instance=podcast)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated podcast", podcast.title)
            messages.success(request, f'"{podcast.title}" was updated.')
            return redirect("podcasts:manage_list")
    else:
        form = PodcastForm(instance=podcast)
    return render(request, "podcasts/podcast_form.html", {"form": form, "mode": "Edit", "podcast": podcast})