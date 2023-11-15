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
    cert_file = forms.FileField(label='Certificado')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=True)

