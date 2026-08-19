from django.shortcuts import redirect
from django.urls import resolve, Resolver404

EXEMPT_URL_NAMES = {"password_change", "logout", "login"}


class ForcePasswordChangeMiddleware:
    """
    If a logged-in user still has must_change_password=True, every request
    (except the password-change page itself, logout, and static/media)
    gets redirected to the password-change form.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated and getattr(user, "must_change_password", False):
            if not (request.path.startswith("/static/") or request.path.startswith("/media/")):
                try:
                    match = resolve(request.path_info)
                    url_name = match.url_name
                except Resolver404:
                    url_name = None

                if url_name not in EXEMPT_URL_NAMES:
                    return redirect("accounts:password_change")

        return self.get_response(request)