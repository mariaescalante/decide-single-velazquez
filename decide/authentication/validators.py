from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)

class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def get_help_text(self):
        return "La contraseña no puede ser demasiado similar a tu información personal."

class CustomMinimumLengthValidator(MinimumLengthValidator):
    def get_help_text(self):
        return "La contraseña debe tener al menos 8 caracteres."

class CustomCommonPasswordValidator(CommonPasswordValidator):
    def get_help_text(self):
        return "La contraseña no puede ser una contraseña común."

class CustomNumericPasswordValidator(NumericPasswordValidator):
    def get_help_text(self):
        return "La contraseña no puede ser completamente numérica."
