from django.test import Client, TestCase
from datetime import datetime
from django.http import HttpRequest
import pytz
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from authentication.models import ActividadInicioSesion, CustomUser, UserChange
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import time
from django.urls import reverse
from rest_framework.authtoken.models import Token
from base import mods
from django.test import override_settings
from django.core import mail
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone
from utils.datetimes import get_datetime_now_formatted
from utils.email import send_email_login_notification
from django.core.files.uploadedfile import SimpleUploadedFile
from authentication.forms import CustomAuthenticationForm
from unittest.mock import patch


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        u = CustomUser(username='voter1')
        u.set_password('123')
        u.save()

        u2 = CustomUser(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

        u3 = CustomUser(username='rafaeldavidgg', email='rafaeldgarciagalocha@gmail.com')
        u3.set_password('decidepass123')
        u3.last_password_change = timezone.now()
        u3.save()

        

    def tearDown(self):
        self.client = None
        
    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )
        
    def test_bloqueo_login(self):
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})     
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '123'})     
        self.assertEqual(response.status_code, 302)
        
    def test_bloqueo_login_reinicio(self):
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.assertEqual(response.status_code, 200)
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login2/', data)
        self.assertEqual(response.status_code, 302)
        self.client.get('/authentication/logout/')
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '123'})
        self.assertEqual(response.status_code, 302)
        
        
    def test_bloqueo_login_wrong(self):
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})  
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})  
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.assertEqual(response.status_code, 200)
        

    def test_bloqueo_login_timed(self):
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.assertEqual(response.status_code, 200)
        time.sleep(2)
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '123'})
        self.assertEqual(response.status_code, 200)


    def test_password_reset_email(self):
        protocol = 'http'
        domain = '127.0.0.1:8000'
        uid = 'uid123'
        token = 'token123'
        email = 'rafaeldgarciagalocha@gmail.com'
        username = 'rafaeldavidgg'

        user = CustomUser.objects.get(email=email, username=username)

        html_message = render_to_string('password_reset_email.html', {
            'email': email,
            'protocol': protocol,
            'domain': domain,
            'uid': uid,
            'token': token,
            'user': user,
        })

        subject = 'Password reset on 127.0.0.1:8000'
        from_email = 'decidevelazquez@gmail.com'
        recipient_list = [email]

        reset_link = f'{protocol}://{domain}{reverse("password_reset_confirm2", kwargs={"uidb64": uid, "token": token})}'
        expected_text = f'Alguien solicitó restablecer la contraseña del correo electrónico {email}.\nHaz click en el siguiente link:\n{reset_link}\nTu nombre de usuario, en caso de que lo hayas olvidado: {user.get_username()}'

        mail.send_mail(
            subject,
            expected_text,
            from_email,
            recipient_list,
            html_message=html_message
        )

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, subject)
        self.assertEqual(sent_mail.from_email, from_email)
        self.assertEqual(sent_mail.to, recipient_list)
        self.assertIn(expected_text, sent_mail.body)

    def test_password_reset_email_missing_email(self):
        protocol = 'http'
        domain = '127.0.0.1:8000'
        uid = 'uid123'
        token = 'token123'
        email = ''
        username = 'usuario_sin_correo'

        html_message = render_to_string('password_reset_email.html', {
            'email': email,
            'protocol': protocol,
            'domain': domain,
            'uid': uid,
            'token': token,
            'user': None,
        })

        subject = 'Password reset on 127.0.0.1:8000'
        from_email = 'decidevelazquez@gmail.com'
        recipient_list = [email]

        with patch('django.core.mail.send_mail') as mock_send_mail:
            mock_send_mail.return_value = None

            mail.send_mail(
                subject,
                'Cuerpo del correo',
                from_email,
                recipient_list,
                html_message=html_message
            )

            self.assertTrue(mock_send_mail.called)
            self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_email_invalid_email(self):
        protocol = 'http'
        domain = '127.0.0.1:8000'
        uid = 'uid123'
        token = 'token123'
        email = 'correo_invalido'
        username = 'usuario'

        html_message = render_to_string('password_reset_email.html', {
            'email': email,
            'protocol': protocol,
            'domain': domain,
            'uid': uid,
            'token': token,
            'user': None,
        })

        subject = 'Password reset on 127.0.0.1:8000'
        from_email = 'decidevelazquez@gmail.com'
        recipient_list = [email]

        with patch('django.core.mail.send_mail') as mock_send_mail:
            mock_send_mail.return_value = None

            mail.send_mail(
                subject,
                'Cuerpo del correo',
                from_email,
                recipient_list,
                html_message=html_message
            )

            self.assertTrue(mock_send_mail.called)
            self.assertEqual(len(mail.outbox), 0)



    def test_password_change_required_1(self):
        data = {'username': 'rafaeldavidgg', 'password': 'decidepass123'}
        response = self.client.post('/authentication/login2/', data, format='json')
        self.assertEqual(response.status_code, 200)

        user = CustomUser.objects.get(username='rafaeldavidgg')
        user.last_password_change -= timedelta(days=10)
        user.save()

        response = self.client.post('/authentication/logout2/')
        self.assertEqual(response.status_code, 302)

        data = {'username': 'rafaeldavidgg', 'password': 'decidepass123'}
        response = self.client.post('/authentication/login2/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.should_change_password(user))

        user.last_password_change = timezone.now()
        user.save()

    def test_password_change_required_2(self):
        # El usuario no ha iniciado sesión recientemente
        data = {'username': 'rafaeldavidgg', 'password': 'decidepass123'}
        response = self.client.post('/authentication/login2/', data, format='json')
        self.assertEqual(response.status_code, 200)

        user = CustomUser.objects.get(username='rafaeldavidgg')
        user.last_login = timezone.now() - timedelta(days=15)
        user.last_password_change -= timedelta(days=30)
        user.save()

        response = self.client.post('/authentication/logout2/')
        self.assertEqual(response.status_code, 302)

        data = {'username': 'rafaeldavidgg', 'password': 'decidepass123'}
        response = self.client.post('/authentication/login2/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.should_change_password(user))

    def test_password_change_required_negative(self):
        # El usuario ha cambiado la contraseña en los últimos 7 días
        data = {'username': 'rafaeldavidgg', 'password': 'newpassword'}
        response = self.client.post('/authentication/login2/', data, format='json')
        self.assertEqual(response.status_code, 200)

        user = CustomUser.objects.get(username='rafaeldavidgg')
        user.last_password_change = timezone.now() - timedelta(days=5)
        user.save()

        response = self.client.post('/authentication/logout2/')
        self.assertEqual(response.status_code, 302)

        data = {'username': 'rafaeldavidgg', 'password': 'newpassword'}
        response = self.client.post('/authentication/login2/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.should_change_password(user))

    def should_change_password(self, user):
        last_change = user.last_password_change
        last_change = last_change.astimezone(timezone.get_current_timezone()) if last_change else None

        X = timedelta(minutes=10080)  # 7 dias
        return last_change and (timezone.now() - last_change) >= X


class RegistroEmailTest(TestCase):

    def test_registro_email_success(self):
        data = {
            'email': 'usuariodeprueba@gmail.com',
            'password1': 'pruebapass123',
            'password2': 'pruebapass123'
        }
        response = self.client.post('/authentication/register_email/', data)

        self.assertEqual(response.status_code, 302)
        
        user_created = CustomUser.objects.get(email='usuariodeprueba@gmail.com')
        
        self.assertTrue(user_created.is_authenticated)
        self.assertEqual(user_created.username,data['email'])
        self.assertEqual(user_created.email,data['email'])
        self.assertEqual(user_created.first_name,'')
        self.assertEqual(user_created.last_name,'')

    def test_registro_email_bad_email(self):
        data = {
            'email': 'BadEmail',
            'password1': 'pruebapass123',
            'password2': 'pruebapass123'
        }
        response = self.client.post('/authentication/register_email/', data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

        user_created = CustomUser.objects.filter(email='BadEmail')

        self.assertFalse(user_created.exists())
    

    def test_registro_email_bad_password(self):
        data_password2_empty = {
            'email': 'emailPruebaPassword2@gmail.com',
            'password1': 'pruebapass123',
            'password2': ''
        }
        response = self.client.post('/authentication/register_email/', data_password2_empty)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

        user_created = CustomUser.objects.filter(email='emailPruebaPassword2@gmail.com')

        self.assertFalse(user_created.exists())


        data_password1_empty = {
            'email': 'emailPruebaPassword1@gmail.com',
            'password1': '',
            'password2': 'pruebapass123'
        }
        response = self.client.post('/authentication/register_email/', data_password1_empty)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

        user_created = CustomUser.objects.filter(email='emailPruebaPassword1@gmail.com')

        self.assertFalse(user_created.exists())
   

        data_distinct_passwords = {
            'email': 'emailPruebaDistinct@gmail.com',
            'password1': 'pruebapass456',
            'password2': 'pruebapass123'
        }
        response = self.client.post('/authentication/register_email/', data_distinct_passwords)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

        user_created = CustomUser.objects.filter(email='emailPruebaDistinct@gmail.com')

        self.assertFalse(user_created.exists())


        data_simple_passwords = {
            'email': 'emailPruebaSimple@gmail.com',
            'password1': 'emailPrueba',
            'password2': 'emailPrueba'
        }
        response = self.client.post('/authentication/register_email/', data_simple_passwords)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

        user_created = CustomUser.objects.filter(email='emailPruebaSimple@gmail.com')

        self.assertFalse(user_created.exists())
        

    def test_registro_email_already_taken(self):
        data = {
            'email': 'usuarioNuevo@gmail.com',
            'password1': 'pruebapass123',
            'password2': 'pruebapass123'
        }
        response = self.client.post('/authentication/register_email/', data)
        user_created = CustomUser.objects.get(email='usuarioNuevo@gmail.com')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_created.username, data['email'])

        response = self.client.post('/authentication/register_email/', data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

        
class CertLoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.url = reverse('cert_login')
        self.cert_path = 'authentication/test_data/secreto001.p12'
        self.cert_name = 'secreto001.p12'
        
    def test_cert_login_view_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cert_login.html')
        self.assertIsInstance(response.context['form'], CustomAuthenticationForm)

    def test_cert_login_view_success(self):

        with open(self.cert_path, 'rb') as file:
            cert_file = SimpleUploadedFile(self.cert_name, file.read())
        
        data = {
            'cert_file': cert_file,
            'password': 'secreto001',
        }

        response = self.client.post(self.url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))

        user = self.user_model.objects.filter(username='00000000A').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)

    def test_cert_login_view_error(self):

        with open(self.cert_path, 'rb') as file:
            cert_file = SimpleUploadedFile(self.cert_name, file.read())
        
        data = {
            'cert_file': cert_file,
            'password': 'tu_password_erroneo',
        }

        response = self.client.post(self.url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Error al procesar el certificado')

        user = self.user_model.objects.filter(username='00000000A').first()
        self.assertIsNone(user)
        
class DateFormattingTestCase(TestCase):
        
    def setUp(self):
        self.fecha_hora_utc = datetime.utcnow()
        self.fecha_hora_utc = pytz.utc.localize(self.fecha_hora_utc)
        self.zona_horaria_local_correcta = pytz.timezone('Europe/Madrid')
        self.fecha_hora_local_correcta = self.fecha_hora_utc.astimezone(self.zona_horaria_local_correcta)

    def test_positive_get_datetime_now_formatted(self):
        resultado = get_datetime_now_formatted()

        formato_deseado = "%B %d at %I:%M %p"
        fecha_formateada_esperada = self.fecha_hora_local_correcta.strftime(formato_deseado)

        self.assertEqual(resultado, fecha_formateada_esperada)

    def test_negative_get_datetime_now_formatted(self):
        resultado = get_datetime_now_formatted()

        formato_deseado_incorrecto = "%Y-%m-%d %H:%M:%S"
        fecha_formateada_esperada_incorrecta = self.fecha_hora_utc.strftime(formato_deseado_incorrecto)

        self.assertNotEqual(resultado, fecha_formateada_esperada_incorrecta)


class TestEmailNotification(TestCase):
    
    def setUp(self):
        self.user = CustomUser(username='testuser', email='testuser@example.com')
        self.user.set_password('qwerty')
        self.user.save()
        
    def test_send_email_on_login_notification(self):
        response = self.client.post(reverse('login2'), {'username': self.user.username, 'password': 'qwerty'})
        # Verifica que se haya enviado el correo electrónico
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Nuevo inicio de sesión')


    def test_send_email_notification(self):

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = user_agent
        request.user = self.user

        template = 'email_notificacion.html'
        subject = 'Asunto del Correo'
        send_email_login_notification(request, template, subject)

        # Se envia a un solo correo
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, subject)
        self.assertEqual(sent_email.from_email, 'decidevelazquez@gmail.com')
        self.assertEqual(sent_email.to, [self.user.email])

        expected_context = {
            'nombre': self.user.username,
            'direccion_ip': '127.0.0.1',
            'agente_usuario': user_agent,
            'fecha_actual': get_datetime_now_formatted(),
        }
        
        expected_html_message = render_to_string(template, expected_context)
        self.assertEqual(sent_email.alternatives[0][0], expected_html_message)

class EditarPerfil(TestCase):
    
    def setUp(self):
        self.user = CustomUser(username='noadmin')
        self.user.set_password('qwerty')
        self.user.save()
        
    def authenticate_user(self):
        self.client.force_login(self.user)

    def test_editar_perfil_GET_restringido(self):
        response = self.client.get(reverse('editar_perfil'))
        self.assertRedirects(response, '/authentication/login2/?next=/authentication/cuenta/editar_perfil/')
 
    def test_editar_perfil_GET_autorizado(self):
        self.authenticate_user()
        
        response = self.client.get(reverse('editar_perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_editar_perfil(self):
        self.authenticate_user()

        url = reverse('editar_perfil')
        
        success_url = reverse('cuenta')
        
        nuevos_datos = {
            'username':'testuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo_usuario@example.com',
        }

        response = self.client.post(url, nuevos_datos)
        
        self.assertRedirects(response, success_url)

        self.assertEqual(response.status_code, 302)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, nuevos_datos['first_name'])
        self.assertEqual(self.user.last_name, nuevos_datos['last_name'])
        self.assertEqual(self.user.email, nuevos_datos['email'])


class RegistroCambiosTest(TestCase):
    
    def setUp(self):
        self.user = CustomUser(username='usuario_original')
        self.user.set_password('user12345')
        self.user.save()
        
    def authenticate_user(self):
        self.client.force_login(self.user)

    
    def test_registro_cambios(self):
        self.authenticate_user()

        url = reverse('editar_perfil')
                
        nuevos_datos = {
            'username':'usuario_original',
            'first_name': 'Usuario',
            'last_name': 'Editado',
            'email': 'usaurio_editado@gmail.com',
        }

        self.client.post(url, nuevos_datos)
        
        self.user.refresh_from_db()
        user_change_first_name = UserChange.objects.get(usuario=self.user, campo_modificado='first_name')
        user_change_last_name = UserChange.objects.get(usuario=self.user, campo_modificado='last_name')
        user_change_email = UserChange.objects.get(usuario=self.user, campo_modificado='email')

        self.assertEqual(user_change_first_name.dato_anterior, '')
        self.assertEqual(user_change_first_name.dato_nuevo, 'Usuario')
        
        self.assertEqual(user_change_last_name.dato_anterior, '')
        self.assertEqual(user_change_last_name.dato_nuevo, 'Editado')

        self.assertEqual(user_change_email.dato_anterior, '')
        self.assertEqual(user_change_email.dato_nuevo, 'usaurio_editado@gmail.com')

    def test_cambio_username_and_login(self):
        self.authenticate_user()

        url = reverse('editar_perfil')
                
        nuevos_datos = {
            'username':'usuario_editado',
            'first_name': '',
            'last_name': '',
            'email': 'usaurio_editado@gmail.com',
        }

        self.client.post(url, nuevos_datos)
        
        self.user.refresh_from_db()
        user_change_username = UserChange.objects.get(usuario=self.user, campo_modificado='username')
        
        self.assertEqual(user_change_username.dato_anterior, 'usuario_original')
        self.assertEqual(user_change_username.dato_nuevo, 'usuario_editado')


        login_datos_correctos = {'username': 'usuario_editado', 'password': 'user12345'}
        response = self.client.post('/authentication/login/', login_datos_correctos)
        self.assertEqual(response.status_code, 200)

        login_datos_erroneos = {'username': 'usuario_original', 'password': 'user12345'}
        response = self.client.post('/authentication/login/', login_datos_erroneos)
        self.assertEqual(response.status_code, 400)

class DeleteAccountViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser(username='testuser')
        self.user.set_password('testpassword')
        self.user.save()
        self.RESTRINGED_VIEW = '/authentication/login2/?next=/authentication/confirmar_borrar_cuenta/'

    def authenticate_user(self):
        self.client.force_login(self.user)

    def test_delete_account_view(self):
        self.authenticate_user()
        url = reverse('confirmar_borrar_cuenta')
        url2 = reverse('borrar_cuenta')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '¿Estás seguro de que quieres eliminar tu cuenta?')

        response = self.client.post(url2)

        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('login2'))
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_cancel_delete_account_view(self):
        self.authenticate_user()
        url = reverse('confirmar_borrar_cuenta')
        url2 = reverse('borrar_cuenta')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '¿Estás seguro de que quieres eliminar tu cuenta?')

        self.assertEqual(CustomUser.objects.count(), 1)

    def test_delete_account_without_login(self):
        url = reverse('confirmar_borrar_cuenta')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.RESTRINGED_VIEW)
        self.assertTrue(self.user.is_authenticated)

class ActividadInicioSesionTest(TestCase):
    
    def setUp(self):
        self.user = CustomUser(username='test_user')
        self.user.set_password('user12345')
        self.user.save()
        
    def authenticate_user(self):
        self.client.force_login(self.user)
        
    def test_positive_login(self):
        data = {'username': 'test_user', 'password': 'user12345'}
        response = self.client.post('/authentication/login2/', data, format='json')

        self.assertEqual(response.status_code, 302)

        ultima_actividad = ActividadInicioSesion.objects.filter(usuario=self.user).latest('fecha')

        self.assertTrue(ultima_actividad.exito)


    def test_negative_login(self):
        data = {'username': 'test_user', 'password': 'fallido'}
        response = self.client.post('/authentication/login2/', data, format='json')

        self.assertEqual(response.status_code, 200)

        ultima_actividad = ActividadInicioSesion.objects.filter(usuario=self.user).latest('fecha')

        self.assertFalse(ultima_actividad.exito)
        
    def test_authenticated_vista_actividad(self):
        ActividadInicioSesion.objects.create(usuario=self.user, exito=True)
        ActividadInicioSesion.objects.create(usuario=self.user, exito=False)
        
        self.authenticate_user()

        response = self.client.get(reverse('actividad'))

        self.assertEqual(response.status_code, 200)

        actividades = response.context['actividades']
        self.assertEqual(actividades.paginator.count, 2)
    
    def test_anon_vista_actividad(self):
        ActividadInicioSesion.objects.create(usuario=self.user, exito=True)
        ActividadInicioSesion.objects.create(usuario=self.user, exito=False)

        response = self.client.get(reverse('actividad'))

        self.assertEqual(response.status_code, 302)
    
    def test_paginacion_actividad_sin_pagina(self):
        self.authenticate_user()
        
        url = reverse('actividad') # + '?page=2'
        
        response = self.client.get(url)
        contexto = response.context
        self.assertIn('actividades', contexto)
        actividades_pagina = contexto['actividades']
        self.assertEqual(actividades_pagina.number, 1)
        self.assertContains(response, 'Página 1 de', status_code=200)
    
    def test_paginacion_actividad_con_numero_valido(self):
        self.authenticate_user()
        
        url = reverse('actividad')  + '?page=1'
        
        response = self.client.get(url)
        contexto = response.context
        self.assertIn('actividades', contexto)
        actividades_pagina = contexto['actividades']
        self.assertEqual(actividades_pagina.number, 1)
        self.assertContains(response, 'Página 1 de', status_code=200)
        
    
    def test_paginacion_actividad_pagina_vacia(self):
        self.authenticate_user()
        
        for i in range(10):
            ActividadInicioSesion.objects.create(usuario=self.user, exito=True)
            ActividadInicioSesion.objects.create(usuario=self.user, exito=False)
            
        url = reverse('actividad')  + '?page=30'
        
        response = self.client.get(url)
        contexto = response.context
        self.assertIn('actividades', contexto)
        actividades_pagina = contexto['actividades']
        self.assertEqual(actividades_pagina.number, 4)
        self.assertContains(response, 'Página 4 de', status_code=200)
        
        url = reverse('actividad')  + '?page=-2'
        
        response = self.client.get(url)
        contexto = response.context
        self.assertIn('actividades', contexto)
        actividades_pagina = contexto['actividades']
        self.assertEqual(actividades_pagina.number, 4)
        self.assertContains(response, 'Página 4 de', status_code=200)
