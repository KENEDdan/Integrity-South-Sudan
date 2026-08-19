from .models import Notification


def notifications_processor(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(recipient=request.user)
        return {
            "nav_notifications": qs[:8],
            "nav_unread_count": qs.filter(is_read=False).count(),
        }
    return {}