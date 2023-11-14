from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username
    
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already taken. Please choose another.')
        return email
    

class CustomAuthenticationForm(forms.Form):
    # Ya que ocasionaba la invalidación del form
    cert_file = forms.FileField(label='Certificado')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=True)

    def clean(self):
            cleaned_data = super().clean()

            # Lógica de validación del certificado (ya la tienes implementada)
            # cert_valid = tu_logica_de_validacion(cleaned_data.get('cert_file'))
            
            cert_valid = cleaned_data.get('cert_file')
            password = cleaned_data.get('password')
            cert_valid = True

            if not cert_valid:
                # Agregar un mensaje de error personalizado
                # Esto de por sí no bloquea el POST
                self.add_error(None, 'El certificado no es válido.')

            return cleaned_data

