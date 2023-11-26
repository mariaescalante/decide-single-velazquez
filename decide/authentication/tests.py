from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from .models import CustomUser
from rest_framework.authtoken.models import Token

from base import mods
from django.urls import reverse
from django.test import override_settings
from django.core import mail
from django.template.loader import render_to_string


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = CustomUser(username='voter1')
        u.set_password('123')
        u.save()

        u2 = CustomUser(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

        u3 = CustomUser(username='rafaeldavidgg', email='rafaeldgarciagalocha@gmail.com')
        u3.set_password('decidepass123')
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
        self.assertEqual(user['id'], 1)
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

