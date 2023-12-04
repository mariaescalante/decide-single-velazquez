from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from rest_framework.authtoken.models import Token

from base import mods
from authentication.models import CustomUser
from django.urls import reverse

class AuthTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser', password='12345')
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