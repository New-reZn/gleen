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

class GlobalSettings(SingletonModel):
    name = models.CharField(max_length=100,blank=False,null=False)
    goal = models.CharField(max_length=100,blank=False,null=False)
    image = models.ImageField(upload_to='global',default="global/logo.svg")

    maintenance_mode = models.BooleanField(default=False)
    
    def __str__(self):
        return "Global Settings"

