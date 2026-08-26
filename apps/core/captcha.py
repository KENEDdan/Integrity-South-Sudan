import json
import urllib.parse
import urllib.request

from django.conf import settings

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(request):
    """Verify a Cloudflare Turnstile response server-side.

    Returns True (skips verification) when TURNSTILE_SECRET_KEY isn't set,
    so the forms keep working normally before the key is configured — this
    is a bot filter, not the form's actual access control.
    """
    if not settings.TURNSTILE_SECRET_KEY:
        return True

    token = request.POST.get("cf-turnstile-response", "")
    if not token:
        return False

    data = urllib.parse.urlencode({
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
        "remoteip": request.META.get("REMOTE_ADDR", ""),
    }).encode()

    try:
        with urllib.request.urlopen(TURNSTILE_VERIFY_URL, data=data, timeout=5) as resp:
            result = json.loads(resp.read().decode())
    except Exception:
        return False
    return bool(result.get("success"))
