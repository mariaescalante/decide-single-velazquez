import json
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .serializers import UserSerializer
from .models import CustomUser
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import resolve_url
from django.contrib.auth.views import LoginView
from utils.decrypt_cert import get_cert_data_in_json

@login_required
def home(request):
        data = {
        'form': CustomUserCreationForm(),
        'user': request.user}

        return render(request, "home.html", data)


class Custom_loginView(LoginView):

    def form_valid(self, form):
        # Llamamos al método form_valid de la clase base para realizar la autenticación
        response = super().form_valid(form)


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
            user = User(username=username)
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

                # Accede al contenido del archivo directamente
                cert_content = cert_file.read()
                
                cert_data = json.loads(get_cert_data_in_json(cert_content, password))
                
                first_name = cert_data["givenName"]
                last_name = cert_data["surname"]
                dni = cert_data["commonName"].split(" - ")[1]
                
                # Buscamos si existe el user en la db
                user = CustomUser.objects.filter(username=dni).first()
                
                if not user:
                    user = CustomUser.objects.create_user(username=dni, first_name=first_name, last_name=last_name)
                                    
                user.save()
                    
            # Autentica y loguea al usuario
            authenticate(request, username=user.username)
            login(request, user)

            return redirect(self.success_url)
        
        except Exception as e:
            # Maneja la excepción y agrega un mensaje de error al formulario
            form.add_error(None, f'Error al procesar el certificado: {str(e)}')

        # Manejar el caso en que el formulario no es válido
        return render(request, self.template_name, {'form': form})
