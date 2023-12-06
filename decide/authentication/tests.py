from datetime import datetime
import time
from django.http import HttpRequest
from django.test import TestCase
import pytz
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from authentication.models import CustomUser
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

    def test_password_change_required(self):
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

    def should_change_password(self, user):
        last_change = user.last_password_change
        last_change = last_change.astimezone(timezone.get_current_timezone()) if last_change else None

        X = timedelta(minutes=10080)  # 7 dias
        return last_change and (timezone.now() - last_change) >= X

    def test_registro_email_success(self):
        data = {
            'email': 'rafaeldgarciagalocha@gmail.com',
            'password1': 'decidepass123',
            'password2': 'decidepass123'
        }
        response = self.client.post('/authentication/register_email/', data, format='json')
        self.assertEqual(response.status_code, 200)
        user_created = CustomUser.objects.filter(email='rafaeldgarciagalocha@gmail.com').exists()
        self.assertTrue(user_created)

    def test_registro_email_failure(self):
        data = {
            'email': 'email',
            'password1': 'pass123',
            'password2': 'pass123'
        }
        response = self.client.post('/authentication/register_email/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

    def test_registro_email_already_taken(self):
        data = {
            'email': 'rafaeldgarciagalocha@gmail.com',
            'password1': 'decidepass123',
            'password2': 'decidepass123'
        }
        data2 = {
            'email': 'rafaeldgarciagalocha@gmail.com',
            'password1': 'decidepass123',
            'password2': 'decidepass123'
        }
        response = self.client.post('/authentication/register_email/', data, format='json')
        self.assertEqual(response.status_code, 200)
        user_created = CustomUser.objects.filter(email='rafaeldgarciagalocha@gmail.com').exists()
        self.assertTrue(user_created)

        response = self.client.post('/authentication/register_email/', data2, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha habido un error en el formulario')

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
        print(reverse('login2'))
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
    
