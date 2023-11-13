from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    secret = models.CharField(max_length=255, blank=True, null=True)
