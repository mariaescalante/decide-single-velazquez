from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import os
import pyotp
from authentication.models import CustomUser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AdminTestCase(StaticLiveServerTestCase):


    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
	
        #Opciones de Chrome


        if(os.path.exists(os.path.join(BASE_DIR,'authentication/static/noadmin.png'))):
            os.remove(os.path.join(BASE_DIR,'authentication/static/noadmin.png'))
            
        options = webdriver.ChromeOptions()
        options.headless = False  #Necesario
        

        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_simpleCorrectLogin(self):
        # Abre la ruta del navegador
        self.driver.get(f'{self.live_server_url}/admin/')
        # Busca los elementos y “escribe”
        self.driver.find_element(By.ID, 'id_username').send_keys("admin")
        self.driver.find_element(By.ID, 'id_password').send_keys("qwerty", Keys.ENTER)

        # Verifica que nos hemos logado porque aparece la barra de herramientas superior
        self.assertTrue(len(self.driver.find_elements(By.ID, 'user-tools')) == 1)

    def test_simpleWrongLogin(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, 'id_username').send_keys("WRONG")
        self.driver.find_element(By.ID, 'id_password').send_keys("WRONG")
        self.driver.find_element(By.ID, 'login-form').submit()

        # Si no, aparece este error
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, 'errornote')) == 1)
        time.sleep(5)

    def test_multifactor_Correct(self):
        
        self.driver.get(f'{self.live_server_url}/authentication/login2/')
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.find_element(By.ID,'enlace').click()
        self.driver.find_element(By.ID,'aceptar').send_keys(Keys.ENTER)
        self.driver.find_element(By.ID,'logout').send_keys(Keys.ENTER)
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        usuario = CustomUser.objects.get(username="noadmin")
        totp_object = pyotp.TOTP(usuario.secret)
        totp_object.now()
        self.driver.find_element(By.ID,'codigo').send_keys(totp_object.now(), Keys.ENTER)
        time.sleep(2)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'logout')) == 1)
                
    def test_multifactor_wrong(self):
        self.driver.get(f'{self.live_server_url}/authentication/login2/')
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.find_element(By.ID,'enlace').click()
        self.driver.find_element(By.ID,'aceptar').send_keys(Keys.ENTER)
        self.driver.find_element(By.ID,'logout').send_keys(Keys.ENTER)
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.find_element(By.ID,'codigo').send_keys(totp_object.now(), Keys.ENTER)
        time.sleep(2)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'logout')) == 0)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'codigo')) == 1)
        
