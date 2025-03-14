from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    image = models.ImageField(default="global/user.svg")
    is_admin = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)
    is_reporter = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
