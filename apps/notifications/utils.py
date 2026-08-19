from .models import Notification


def notify(recipient, message, sender=None, link="", related_object=None):
    return Notification.objects.create(
        recipient=recipient, sender=sender, message=message,
        link=link, related_object=related_object,
    )


def notify_role(role, message, sender=None, link="", related_object=None):
    from apps.accounts.models import User
    for recipient in User.objects.filter(role=role, is_active=True):
        notify(recipient, message, sender=sender, link=link, related_object=related_object)