import time
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from base import mods
from authentication.models import CustomUser


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

    def tearDown(self):
        self.client = None


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
              
        self.assertEqual(response.status_code, 302)
        

    def test_bloqueo_login_timed(self):
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '56342523'})
        self.assertEqual(response.status_code, 302)
        time.sleep(2)
        response = self.client.post('/authentication/login2/', {'username': 'voter1', 'password': '123'})
        self.assertEqual(response.status_code, 302)

