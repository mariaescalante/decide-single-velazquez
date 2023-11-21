from datetime import timezone
import datetime
import time
from django import apps
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager, BaseUserManager

class CustomUser(AbstractUser):
    secret = models.CharField(max_length=255, blank=True, null=True)

    class UserManager(BaseUserManager):
        use_in_migrations = True

        def _create_user(self, username, email, password, **extra_fields):
            """
            Create and save a user with the given username, email, and password.
            """
            if not username:
                raise ValueError("The given username must be set")
            email = self.normalize_email(email)
            # Lookup the real model class from the global app registry so this
            # manager method can be used in migrations. This is fine because
            # managers are by definition working on the real model.
            GlobalUserModel = apps.get_model(
                self.model._meta.app_label, self.model._meta.object_name
            )
            username = GlobalUserModel.normalize_username(username)
            user = self.model(username=username, email=email, **extra_fields)
            user.password = make_password(password)
            user.save(using=self._db)
            return user

        def create_user(self, username, email=None, password=None, **extra_fields):
            extra_fields.setdefault("is_staff", False)
            extra_fields.setdefault("is_superuser", False)
            return self._create_user(username, email, password, **extra_fields)

        def create_superuser(self, username, email=None, password=None, **extra_fields):
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_superuser", True)

            if extra_fields.get("is_staff") is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if extra_fields.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")

            return self._create_user(username, email, password, **extra_fields)

            
    def block_account(user):
        """Bloquea una cuenta de usuario.

        Args:
            user: El usuario a bloquear.
        """

        user.active = False
        user.save()


        # Envía un correo electrónico al usuario notificándole que su cuenta ha sido bloqueada.

   ##     send_email(user, "Su cuenta ha sido bloqueada",
     ##               "Su cuenta ha sido bloqueada debido a demasiados intentos fallidos de inicio de sesión. Para desbloquear su cuenta, haga clic en el siguiente enlace: [enlace]"
       ## )