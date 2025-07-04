# core/signals.py

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from gleen.helpers import notify_user
from .models import Issues, Activities

@receiver(m2m_changed, sender=Issues.assignees.through)
def assignees_changed(sender, instance, action, reverse, model, pk_set, **kwargs): 
    actor = getattr(instance, "_acting_user", instance.creator)
    if action == "post_add":
        # Users just assigned
        added = model.objects.filter(pk__in=pk_set)
        for user in added:
            Activities.objects.create(
                issue=instance,
                subject=actor,  # or however you track updater
                verb="assigned issue to",
                object=str(user),
                type="assigned"
            )
            
            payload = {
                    "type": "issue.assigned",
                    "issue_id": instance.id,
                    "message": f"Issue #{instance.id} have been assigned to you",
                }
            
            notify_user(user,payload)
        
    elif action == "post_remove":
        # Users just unassigned
        removed = model.objects.filter(pk__in=pk_set)
        for user in removed:
            Activities.objects.create(
                issue=instance,
                subject=actor,
                verb="unassigned issue from",
                object=str(user),
                type="unassigned"
            )
            
            payload = {
                    "type": "issue.unassigned",
                    "issue_id": instance.id,
                    "message": f"you have been unassigned from Issue #{instance.id}",
                }
            
            notify_user(user,payload)