from django.db import models
from core.models import User 

# Create your models here.
class NotificationPreferences(models.Model):
    user = models.OneToOneField(
        "core.User",
        on_delete=models.CASCADE,
        related_name="notification_preferences"
    )

    # Issue event notifications
    issue_assigned    = models.BooleanField(default=True)
    issue_unassigned  = models.BooleanField(default=True)
    issue_status      = models.BooleanField(default=True)
    issue_priority    = models.BooleanField(default=True)
    issue_type        = models.BooleanField(default=True)  
    issue_pinned      = models.BooleanField(default=True)
    issue_unpinned    = models.BooleanField(default=True)
    issue_locked      = models.BooleanField(default=True)
    issue_unlocked    = models.BooleanField(default=True)
    issue_name        = models.BooleanField(default=True)
    issue_desc        = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Notification prefs for {self.user}"