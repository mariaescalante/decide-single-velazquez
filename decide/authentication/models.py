from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    secret = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        token, created = Token.objects.get_or_create(user=self)
        self.token = token.key
        super().save(*args, **kwargs)

class UserChange(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    dato_anterior = models.CharField(max_length=255, blank=True, null=True)
    dato_nuevo = models.CharField(max_length=255, blank=True, null=True)
    campo_modificado = models.CharField(max_length=255, blank=True, null=True)
    