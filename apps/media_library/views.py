from django.shortcuts import render, redirect
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import MediaResource
from .forms import MediaResourceForm


@role_required("media")
def resource_list(request):
    query = request.GET.get("q", "")
    resources = MediaResource.objects.all()
    if query:
        resources = resources.filter(tags__icontains=query) | resources.filter(title__icontains=query)
    return render(request, "media_library/resource_list.html", {"resources": resources, "query": query})


@role_required("media")
def resource_add(request):
    if request.method == "POST":
        form = MediaResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, f'"{resource.title}" was added to the library.')
            return redirect("media_library:resource_list")
    else:
        form = MediaResourceForm()
    return render(request, "media_library/resource_form.html", {"form": form})