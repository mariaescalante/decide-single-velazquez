import json
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .forms import CustomUserCreationForm, CustomUserCreationFormEmail, CustomPasswordChangeForm, CustomResetPasswordForm, EditarPerfilForm
from .serializers import UserSerializer
from .models import CustomUser, UserChange, ActividadInicioSesion
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import resolve_url
from django.contrib.auth.views import LoginView
from utils.decrypt_cert import get_cert_data_in_json
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse, reverse_lazy
import pyotp
import qrcode
import os
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import AuthenticationForm
from decide.settings import AUTH_MAX_FAILED_LOGIN_ATTEMPTS
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from utils.datetimes import get_datetime_now_formatted
from utils.email import send_email_login_notification
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@login_required
def home(request):
        data = {
        'form': CustomUserCreationForm(),
        'user': request.user}

        return render(request, "home.html", data)

user_failed_login_attempts = 0
usernames = []
class Custom_loginView(LoginView):
    def login2(request):
        """Inicia sesión a un usuario.

        Args:
            request: La solicitud HTTP.

        Returns:
            La respuesta HTTP.
        """
        
        
        global user_failed_login_attempts
        global usernames
        # ...
        
        if request.POST :
            try:
                usuario = CustomUser.objects.get(username=request.POST.get("username"))
            except:
                return redirect("login2")
            if not usuario.is_active:
                # La cuenta está bloqueada.
                
                user_failed_login_attempts = 0
                return render(request, "registro.html", {'form': CustomUserCreationForm ,'mensaje': 'Cuenta bloqueada'})

            elif user_failed_login_attempts >= AUTH_MAX_FAILED_LOGIN_ATTEMPTS and usuario.username in usernames:
                # El límite de intentos fallidos se ha alcanzado.
                         
                usuario = CustomUser.objects.get(username=request.POST.get("username"))
                CustomUser.block_account(usuario)
                

            else:
                # El usuario no existe o la contraseña es incorrecta.
                if(not check_password(request.POST.get("password"), usuario.password) and usuario.username in usernames):
                    user_failed_login_attempts += 1
                    
                    ActividadInicioSesion.objects.create(usuario=usuario, exito=False)
                    
                    return render(request, "registration/login.html", { 'form': AuthenticationForm})
                
                elif not check_password(request.POST.get("password"), usuario.password):
                    usernames.append(usuario.username)
                    user_failed_login_attempts = 0
                    user_failed_login_attempts += 1
                    
                    ActividadInicioSesion.objects.create(usuario=usuario, exito=False)
                    
                    return render(request, "registration/login.html", { 'form': AuthenticationForm})
                else:
                    # El usuario ha iniciado sesión correctamente.
                    user_failed_login_attempts = 0
                    login(request, usuario)
                    send_email_login_notification(request, 'email_notificacion.html', 'Nuevo inicio de sesión')
                    
                    ActividadInicioSesion.objects.create(usuario=usuario)
                    
                    if(usuario.secret):
                        return redirect("comprobarqr", user_id=usuario.id)


                    return redirect("home")
            
                
        return render(request, "registration/login.html", { 'form': AuthenticationForm})
    
    def get_success_url(self):
        user = self.request.user

        
        
        # Verificar si el usuario tiene un dato llamado 'secret'
        if hasattr(user, 'secret') and user.secret:
            user_id = self.request.user.id
            success_url = reverse('comprobarqr', kwargs={'user_id': user_id})
            logout(self.request)
            return success_url 
        
        last_change = user.last_password_change
        last_change = last_change.astimezone(timezone.get_current_timezone()) if last_change else None

        X = timedelta(minutes=10080) # 7 dias
        if last_change and (timezone.now() - last_change) >= X:
            return reverse('password_change2')

        return super().get_success_url()
   
def quitardobleautenticacion(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    user.secret = None
    user.save()
    os.remove(os.path.join(BASE_DIR,f'authentication/static/{user.username}.png'))

    return redirect('home')

def registro(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        if user_creation_form.is_valid():
            user = user_creation_form.save()

            login(request, user)
            return redirect('home')
        else:
            data['mensaje'] = 'Ha habido un error en el formulario'
    return render(request, "registro.html", data)

def registro_email(request):
    data = {
        'form': CustomUserCreationFormEmail()
    }
    if request.method == 'POST':
        user_creation_form = CustomUserCreationFormEmail(data=request.POST)

        if user_creation_form.is_valid():
            user = user_creation_form.save()

            login(request, user)
            return redirect('home')
        else:
            data['mensaje'] = 'Ha habido un error en el formulario'
    return render(request, "registro_email.html", data)


def comprobarqr(request, user_id):
    if(request.method == 'POST'):
        user = CustomUser.objects.get(pk=user_id)
        codigo = request.POST.get('codigo', None)
        totp_object = pyotp.TOTP(user.secret)
        
        if(totp_object.verify(codigo)):
            login(request, user)
            return render(request, 'home.html')
    return render(request, '2fa.html')

@login_required
def dobleautenticacion(request, user_id):

    if(request.method == 'POST'):
        return redirect('home')
    secreto = pyotp.random_base32()
    totp_object = pyotp.TOTP(secreto)
    user = get_object_or_404(CustomUser, id=user_id)
    user.secret = secreto
    user.save()
    qr_texto = totp_object.provisioning_uri(name=request.user.username , issuer_name="Decide App")
    qr = qrcode.make(qr_texto)
    raiz = os.path.join(BASE_DIR, 'authentication/static')
    camino = f'{raiz}/{request.user.username}.png'
    camino_foto = f'/static/{request.user.username}.png'
    qr.save(camino)
    datos = {
        'qr_text' : qr_texto,
        'camino': camino_foto
    }
    return render(request, 'factordoble.html', datos)

class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)


class CertLoginView(LoginView):
    template_name = 'cert_login.html'
    success_url = 'home'

    def get(self, request, *args, **kwargs):
        form = CustomAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomAuthenticationForm(request.POST, request.FILES)

        try:
            if form.is_valid():
                cert_file = request.FILES.get('cert_file')
                password = form.cleaned_data['password']

                cert_content = cert_file.read()
                
                cert_data = json.loads(get_cert_data_in_json(cert_content, password))
                
                first_name = cert_data["givenName"]
                last_name = cert_data["surname"]
                dni = cert_data["commonName"].split(" - ")[1]
                
                user = CustomUser.objects.filter(username=dni).first()
                
                if not user:
                    user = CustomUser.objects.create_user(username=dni, first_name=first_name, last_name=last_name)
                                    
                user.save()
                    
            authenticate(request, username=user.username)
            login(request, user)

            return redirect(self.success_url)
        
        except Exception as e:
            if 'deserialize' in str(e):
                form.add_error(None, f'Formato incorrecto del certificado (debe ser *.p12)')
            if 'password' in str(e):
                form.add_error(None, f'Contraseña incorrecta')
                

        return render(request, self.template_name, {'form': form})
    
@login_required
def cuenta(request):
    user = request.user
    data = {
        'user': user
    }
    return render(request, "cuenta.html", data)


@login_required
def editar_perfil(request):
    user = request.user

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=user)
        if form.is_valid():
            old_user = CustomUser.objects.get(pk=user.pk)
            form.save()
            new_user = CustomUser.objects.get(pk=user.pk)

            for field in form.changed_data:
                old_value = getattr(old_user, field)
                new_value = getattr(new_user, field)
                UserChange.objects.create(
                    usuario=user,
                    campo_modificado=field,
                    dato_anterior=str(old_value),
                    dato_nuevo=str(new_value)
                )
            return redirect('cuenta')
    else:
        form = EditarPerfilForm(instance=user)

    data = {
        'form': form,
        'user': user
    }
    return render(request, "editar_perfil.html", data)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done2')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete2')
    form_class = CustomResetPasswordForm

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('password_change_success2')

    def form_valid(self, form):
        user = self.request.user
        user.last_password_change = timezone.now()
        user.save()

        return super().form_valid(form)

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'password_change_success.html'


def terms_and_conditions(request):
    # Lógica para los términos y condiciones
    return render(request, 'terminos_condiciones.html')

    
@login_required
def confirmar_borrar_cuenta(request):
    return render(request, 'confirmar_borrar_cuenta.html')

@login_required
def borrar_cuenta(request):
    if request.method == 'POST':
        request.user.delete()

        logout(request)

        messages.success(request, 'Tu cuenta ha sido eliminada correctamente.')
        return redirect('login2')

@login_required
def actividad(request):
    actividades = ActividadInicioSesion.objects.filter(usuario=request.user).order_by('-fecha')
    
    ELEMENTS_PER_PAGE = 5
    
    paginator = Paginator(actividades, ELEMENTS_PER_PAGE)  # Muestra 10 actividades por página
    page = request.GET.get('page')

    try:
        actividades_pagina = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, muestra la primera página
        actividades_pagina = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (por ejemplo, 9999), muestra la última página
        actividades_pagina = paginator.page(paginator.num_pages)

    return render(request, 'actividad.html', {'actividades': actividades_pagina})
