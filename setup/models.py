from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class SingletonModel(models.Model):
    class Meta:
        abstract = True  # Makes this an abstract base class

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if self.__class__.objects.exists() and not self.pk:
            raise ValidationError("Only one instance of this model is allowed.")
        super().save(*args, **kwargs)