from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import NewsPost, NewsCategory
from .forms import NewsPostForm, NewsMediaFormSet
from apps.achievements.models import Achievement

def landing_page(request):
    category = request.GET.get("category", "")
    posts = NewsPost.objects.filter(is_published=True).filter(
        Q(display_until__isnull=True) | Q(display_until__gte=timezone.now().date())
    ).filter(
        Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now())
    )
    if category:
        posts = posts.filter(category=category)

    featured_achievements = Achievement.objects.filter(
        is_featured=True, is_published=True
    ).order_by("display_order", "-created_at")

    return render(request, "newsfeed/landing.html", {
        "posts": posts, "categories": NewsCategory.choices, "active_category": category,
        "featured_achievements": featured_achievements,
    })


def post_detail(request, pk):
    post = get_object_or_404(NewsPost, pk=pk, is_published=True)
    return render(request, "newsfeed/post_detail.html", {"post": post})


@role_required("media")
def manage_list(request):
    posts = NewsPost.objects.all()
    return render(request, "newsfeed/manage_list.html", {"posts": posts})

@role_required("media")
def content_calendar(request):
    posts = NewsPost.objects.filter(
        Q(scheduled_for__isnull=False) | Q(created_at__gte=timezone.now())
    ).order_by("scheduled_for", "-created_at")
    return render(request, "newsfeed/calendar.html", {"posts": posts})


@role_required("media")
def post_create(request):
    if request.method == "POST":
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            formset = NewsMediaFormSet(request.POST, request.FILES, instance=post)
            if formset.is_valid():
                formset.save()
            log_action(request.user, "Published news post", post.title)
            messages.success(request, f'"{post.title}" was published.')
            return redirect("newsfeed:manage_list")
    else:
        form = NewsPostForm()
        formset = NewsMediaFormSet()
    return render(request, "newsfeed/post_form.html", {"form": form, "formset": formset, "mode": "Add"})


@role_required("media")
def post_edit(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    if request.method == "POST":
        form = NewsPostForm(request.POST, request.FILES, instance=post)
        formset = NewsMediaFormSet(request.POST, request.FILES, instance=post)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            log_action(request.user, "Updated news post", post.title)
            messages.success(request, f'"{post.title}" was updated.')
            return redirect("newsfeed:manage_list")
    else:
        form = NewsPostForm(instance=post)
        formset = NewsMediaFormSet(instance=post)
    return render(request, "newsfeed/post_form.html", {"form": form, "formset": formset, "mode": "Edit", "post": post})


@role_required("media")
def post_delete(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    if request.method == "POST":
        title = post.title
        post.delete()
        log_action(request.user, "Deleted news post", title)
        messages.success(request, f'"{title}" was deleted.')
        return redirect("newsfeed:manage_list")
    return render(request, "newsfeed/post_confirm_delete.html", {"post": post})