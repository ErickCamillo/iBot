from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from functools import partial
from time import sleep
from random import randint

class Instagram:
    
    def __init__(self, driver):

        self.__browser = driver
        self.__url = r'https://www.instagram.com/'
        self.__browser_wait = WebDriverWait(self.__browser, 10 , poll_frequency=1)

    def __WaitElement(self, locator, wdriver):

        element = wdriver.find_element(*locator)
        if element: return True
        else: return False

    def Login(self, user, password):

        self.__browser.get(self.__url)
        self.__browser_wait.until(partial(self.__WaitElement , (By.NAME , 'username')))

        self.__browser.find_element_by_name('username').send_keys(user)
        self.__browser.find_element_by_name('password').send_keys(password)
        sleep(1)
        self.__browser.find_element_by_class_name('sqdOP').submit()

        try:
            self.__browser_wait.until(partial(self.__WaitElement , (By.ID ,'slfErrorAlert')))
        except TimeoutException:
            return (True, None)
        else:
            error_login = self.__browser.find_element_by_id('slfErrorAlert')
            if error_login:
                message = error_login.text
                return (False , message)
                
    def LoadPage(self, page):

        if self.__url in page:
            self.__browser.get(page)
        else:
            self.__browser.get(self.__url + page)

        # Aguardando o carregamento da pagina
        self.__browser_wait.until(partial(self.__WaitElement , (By.TAG_NAME , 'footer')))

        # Rolando a pagina para baixo
        self.__browser.execute_script('window.scrollBy(0, 120)')

    def PublishComment(self, comment):
        
        self.__browser_wait.until(partial(self.__WaitElement , (By.CLASS_NAME , 'Ypffh')))
        input_comment = self.__browser.find_element_by_class_name('Ypffh')
        input_comment.click()

        try:
            input_comment.send_keys(comment)
        except StaleElementReferenceException:
            input_comment = self.__browser.find_element_by_class_name('Ypffh')
            input_comment.click()
            input_comment.send_keys(comment)

        sleep(randint(a=2, b=10))
        try:
            self.__browser.find_element_by_xpath("//button[contains(text(),'Publicar')]").click()
        except ElementClickInterceptedException:
            raise ElementClickInterceptedException

    def Refresh(self):
        self.__browser.refresh()

    def Close(self):
        self.__browser.quit()

