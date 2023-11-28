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
import pyautogui

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
        options.add_experimental_option("prefs", {"toolbar.theme.color": "dark"})
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
        

        ventanas = self.driver.window_handles

        # Cambiar a la segunda ventana
        self.driver.switch_to.window(ventanas[1])
        
        time.sleep(1.5)
        self.driver.get('chrome://settings')
        time.sleep(1.5)
        try:
            persona = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/persona.png"), confidence= 0.75)
            pyautogui.click(persona)
            time.sleep(0.5)
            color = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/cambio_color.png"), confidence= 0.75)
            pyautogui.click(color)
        except pyautogui.ImageNotFoundException:
             pass
        time.sleep(0.5)
        self.driver.switch_to.window(ventanas[0])

        time.sleep(2)
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.find_element(By.ID,'enlace').click()
        time.sleep(1)
        extn = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/fijar.png"))
        pyautogui.click(extn)
        time.sleep(1)
        try:
            codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension.png"), confidence= 0.75)
            pyautogui.click(codigo)
        except pyautogui.ImageNotFoundException:
            codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension2.png"), confidence= 0.75)
            pyautogui.click(codigo) 
        time.sleep(3)
        añadir = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/añadir_qr.png"), confidence= 0.6)
        pyautogui.click(añadir)
        time.sleep(1)
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
        try:
            codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension.png"), confidence= 0.75)
            pyautogui.click(codigo)
        except pyautogui.ImageNotFoundException:
            codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension2.png"), confidence= 0.75)
            pyautogui.click(codigo) 
        time.sleep(1)
        decide = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/decideapp.png"), confidence= 0.75)
        pyautogui.click(decide)
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)
        input_ = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/input.png"), confidence= 0.65)
        pyautogui.click(input_)
        time.sleep(0.5)
        pyautogui.keyDown('ctrl')
        pyautogui.press('v')
        pyautogui.keyUp('ctrl')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'logout')) == 1)
                
        
    def test_multifactor_wrong(self):
        self.driver.get(f'{self.live_server_url}/authentication/login2/')
        time.sleep(8)
        

        ventanas = self.driver.window_handles

        # Cambiar a la segunda ventana
        self.driver.switch_to.window(ventanas[1])
        
        time.sleep(1.5)
        self.driver.get('chrome://settings')
        time.sleep(1.5)
        try:
            persona = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/persona.png"), confidence= 0.75)
            pyautogui.click(persona)
            time.sleep(0.5)
            color = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/cambio_color.png"), confidence= 0.75)
            pyautogui.click(color)
        except pyautogui.ImageNotFoundException:
             pass
        time.sleep(0.5)
        self.driver.switch_to.window(ventanas[0])

        time.sleep(2)
        self.driver.find_element(By.ID,'id_username').send_keys("noadmin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        self.driver.find_element(By.ID,'enlace').click()
        time.sleep(1)
        extn = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/fijar.png"))
        pyautogui.click(extn)
        time.sleep(1)
        try:
            codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension.png"), confidence= 0.75)
            pyautogui.click(codigo)
        except pyautogui.ImageNotFoundException:
            codigo = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/extension2.png"), confidence= 0.75)
            pyautogui.click(codigo) 
        time.sleep(3)
        añadir = pyautogui.locateOnScreen(os.path.join(BASE_DIR, "authentication/static/añadir_qr.png"), confidence= 0.6)
        pyautogui.click(añadir)
        time.sleep(1)
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
        self.assertTrue(len(self.driver.find_elements(By.ID, 'logout')) == 0)