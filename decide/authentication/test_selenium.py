from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import pyautogui

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AdminTestCase(StaticLiveServerTestCase):


    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
	
        #Opciones de Chrome


        options = webdriver.ChromeOptions()
        options.headless = False #Necesario
        options.add_extension(os.path.join(BASE_DIR,'Authenticator.crx'))
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
        time.sleep(8)
        
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        
        self.driver.find_element(By.ID,'enlace').click()
        time.sleep(1)
        inicio = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/inicio.png"), confidence= 0.75)
        pyautogui.click(inicio)
        time.sleep(1)
        extn = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/fijar.png"))
        pyautogui.click(extn)
        time.sleep(1)
        codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension.png"), confidence= 0.75)
        pyautogui.click(codigo)
        time.sleep(3)
        añadir = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/añadir_qr.png"), confidence= 0.6)
        pyautogui.click(añadir)
        time.sleep(1)
        home = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/dashboard.png"), confidence= 0.75)
        pyautogui.moveTo(100, 300, duration=1)
        pyautogui.mouseDown()
        pyautogui.moveTo(900, 1000, duration=1)
        time.sleep(1)
        pyautogui.mouseUp()
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)
        self.driver.find_element(By.ID,'aceptar').send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.find_element(By.ID,'logout').send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        extn = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/fijar.png"))
        pyautogui.click(extn)
        time.sleep(1)
        codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension.png"), confidence= 0.75)
        pyautogui.click(codigo)
        time.sleep(1)
        decide = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/decideapp.png"), confidence= 0.75)
        pyautogui.click(decide)
        time.sleep(1)
        pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(1)
        input_ = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/input.png"), confidence= 0.75)
        pyautogui.click(input_)
        pyautogui.keyDown('ctrl')
        pyautogui.press('v')
        pyautogui.keyUp('ctrl')
        pyautogui.press('enter')
        time.sleep(2)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'logout')) == 1)
                
        
    def test_multifactor_wrong(self):
        self.driver.get(f'{self.live_server_url}/authentication/login2/')
        time.sleep(8)
        
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        
        self.driver.find_element(By.ID,'enlace').click()
        time.sleep(1)
        inicio = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/inicio.png"), confidence= 0.75)
        pyautogui.click(inicio)
        time.sleep(1)
        extn = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/fijar.png"))
        pyautogui.click(extn)
        time.sleep(1)
        codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension.png"), confidence= 0.75)
        pyautogui.click(codigo)
        time.sleep(3)
        añadir = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/añadir_qr.png"), confidence= 0.6)
        pyautogui.click(añadir)
        time.sleep(1)
        home = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/dashboard.png"), confidence= 0.75)
        pyautogui.moveTo(100, 300, duration=1)
        pyautogui.mouseDown()
        pyautogui.moveTo(900, 1000, duration=1)
        time.sleep(1)
        pyautogui.mouseUp()
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)
        self.driver.find_element(By.ID,'aceptar').send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.find_element(By.ID,'logout').send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.find_element(By.ID, 'codigo').send_keys("fhasjñfas", Keys.ENTER)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'logout')) == 0)

