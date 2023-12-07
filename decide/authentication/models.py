from datetime import timezone
import datetime
import time
from django import apps
from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager, BaseUserManager

class CustomUser(AbstractUser):
    secret = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.last_password_change = timezone.now()
        super().save(*args, **kwargs)
        token, created = Token.objects.get_or_create(user=self)
        self.token = token.key
        super().save(*args, **kwargs)
        
    def block_account(user):
        """Bloquea una cuenta de usuario.

        Args:
            user: El usuario a bloquear.
        """

        user.is_active = False
        user.save()


