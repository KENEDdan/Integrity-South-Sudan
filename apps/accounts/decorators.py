from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Restricts a view to the given roles. Super Admin is always allowed,
    on every role-restricted view, site-wide.
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_super_admin:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator