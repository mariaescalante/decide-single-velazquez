from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm, AuthenticationForm
from .models import CustomUser
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm):
    accepted_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label='He leído y acepto los términos y condiciones'
    )    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'accepted_terms') 
  
class CustomUserCreationFormEmail(UserCreationForm):
    accepted_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label='He leído y acepto los términos y condiciones'
    )    
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'accepted_terms')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already taken. Please choose another.')
        return email  

class CustomAuthenticationForm(forms.Form):
    cert_file = forms.FileField(
        label='Certificado',
        help_text="El certificado debe tener extensión .p12",
        widget=forms.ClearableFileInput(attrs={'accept': '.p12'})
    )
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=True)

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data
    
class CustomResetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.last_password_change = timezone.now()
        if commit:
            user.save()
        return user

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email',
            'username':'Nombre de Usuario'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email or '@' not in email:
            raise forms.ValidationError("Por favor, introduce un email válido.")
        
        return email

