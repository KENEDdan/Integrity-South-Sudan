from django.conf import settings


def turnstile_processor(request):
    return {"TURNSTILE_SITE_KEY": settings.TURNSTILE_SITE_KEY}
