from .models import AuditLogEntry


def log_action(actor, action, details=""):
    AuditLogEntry.objects.create(actor=actor, action=action, details=details)