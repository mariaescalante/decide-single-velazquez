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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AdminTestCase(StaticLiveServerTestCase):


    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
    
        #Opciones de Chrome

        options = webdriver.ChromeOptions()
        options.headless = False #Necesario
        if(os.path.exists(os.path.join(BASE_DIR,'authentication/static/noadmin.png'))):
            os.remove(os.path.join(BASE_DIR,'authentication/static/noadmin.png'))        
        options.add_extension(os.path.join(BASE_DIR,'Authenticator.crx'))
        desired_cap = {
        'browser': 'Chrome',
        'browser_version': 'latest',
        'os': 'Windows',
        'os_version': '10',
        'resolution': '1920x1080',
        'name': 'Ejemplo de prueba en BrowserStack',
        'url': 'http://localhost:8000',  # Update this URL
    }

        options.set_capability('bstack:options', desired_cap)
        

        self.driver = webdriver.Remote(
        command_executor='https://alejandrogarca_1LS0NP:ZUMcNpmcRBkQ5QrPPvyx@hub-cloud.browserstack.com/wd/hub',
        desired_capabilities=desired_cap
    )
        

        super().setUp()


    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_simpleCorrectLogin(self):
        # Abre la ruta del navegador
        self.driver.get(f'http://localhost:8000/admin/')
        # Busca los elementos y “escribe”
        self.driver.find_element(By.ID, 'id_username').send_keys("admin")
        self.driver.find_element(By.ID, 'id_password').send_keys("qwerty", Keys.ENTER)

        # Verifica que nos hemos logado porque aparece la barra de herramientas superior
        self.assertTrue(len(self.driver.find_elements(By.ID, 'user-tools')) == 1)

    def test_simpleWrongLogin(self):
        self.driver.get(f'http://localhost:8000/admin/')
        self.driver.find_element(By.ID, 'id_username').send_keys("WRONG")
        self.driver.find_element(By.ID, 'id_password').send_keys("WRONG")
        self.driver.find_element(By.ID, 'login-form').submit()

        # Si no, aparece este error
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, 'errornote')) == 1)
        time.sleep(5)

