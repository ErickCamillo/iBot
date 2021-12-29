from sys import stderr
from requests import Session
from bs4 import BeautifulSoup
from re import search
from json import load, dump
from os.path import basename
from selenium.webdriver import Firefox , Chrome, Edge
from Modules.utils import WebDriverUtils ,GetBrowserInfoException

class WebDriverBase:
    
    def __init__(self, browserinfo=None):

        if browserinfo != None:
            self.name = browserinfo['name']
            self.url_download = browserinfo['url_download']
            self.version = browserinfo['version']
            self.os = browserinfo['os']

    # Retorna o link de download e nome do webdriver
    def __PageParser(self, page):

        # <Firefox>
        if self.name == 'firefox':
            box = page.find('div', class_='Box-body')
            webdriver_version = box.find('a', class_='Link--primary').text

            if self.os == 'win32':
                webdriver_title = 'geckodriver-v{}-win64.zip'.format(webdriver_version)
            elif self.os == 'linux' or self.os == 'linux2':
                webdriver_title = 'geckodriver-v{}-linux64.tar.gz'.format(webdriver_version)

            for li in page.find_all('li', class_='Box-row'):
                if li.a.span.get_text() == webdriver_title:
                    url_download = search(r'(\w+.//\w+.\w+)', self.url_download).group() + li.a['href']
                    return (webdriver_title , url_download)
        # </Firefox>
        
        # <Chrome>
        elif self.name == 'chrome':
            if self.os == 'win32':
                webdriver_title = 'chromedriver_win32.zip'
            elif self.os == 'linux' or self.os == 'linux2':
                webdriver_title = 'chromedriver_linux64.zip'

            spans = page.find_all('span', class_='aw5Odc')
            for span in spans:
                webdriver_version = span.a.text.split(' ')[1]
                webdriver_version_firstnumber = search(r'([0-9])+', webdriver_version).group(0)
                browser_version_firstnumber = search(r'([0-9])+', self.version).group(0)
                if browser_version_firstnumber == webdriver_version_firstnumber:
                    url_download = span.a['href'] + webdriver_title
                    url_download = url_download.replace('index.html?path=', '')
                    return (webdriver_title , url_download)
        # </Chrome>
        
        # <Edge>
        # Implementado o uso do webdriver edge apenas no windows
        elif self.name == 'msedge':
            elements_p = page.find_all('p', class_='driver-download__meta')
            for p in elements_p:
                webdriver_version = p.text
                webdriver_version_firstnumber = search(r'([0-9])+', webdriver_version).group(0)
                browser_version_firstnumber = search(r'([0-9])+', self.version).group(0)
                if browser_version_firstnumber == webdriver_version_firstnumber:
                    for a in p.find_all('a'):
                        if a.text == 'x64':
                            url_download = a['href']
                            webdriver_title = basename(url_download)
                            return (webdriver_title , url_download)
        # </Edge>

    def DownloadWebDriver(self, path):

        request = Session()
        response = request.get(self.url_download)
        if response.status_code != 200:
            print('[ERRO] Não foi possivel acessar a pagina de download do webdriver: {0}:{1}'
            .format(self.browsername , self.url_download), file=stderr)
            return (response.status_code, None)

        page = BeautifulSoup(response.text , 'html.parser')

        webdriver_name , url_download = self.__PageParser(page)
        driver = request.get(url_download)
        if driver.status_code != 200:
            print('[ERRO] Não foi possivel fazer o download do webdriver: {}'.format(webdriver_name), file=stderr)
            return (driver.status_code,None)
        with open(path + webdriver_name , 'wb') as file:
            file.write(driver.content)

        return (200, webdriver_name)

class FirefoxWebDriver(WebDriverBase):

    def __init__(self, binfo=None):

        WebDriverBase.__init__(self, browserinfo=binfo)

    def WebDriver(self, path):

        self.driver = Firefox(executable_path=path)
        return self.driver
        
class ChromeWebDriver(WebDriverBase):

    def __init__(self, binfo=None):

        WebDriverBase.__init__(self, browserinfo=binfo)

    def WebDriver(self, path):

        self.driver = Chrome(executable_path=path)
        return self.driver

class EdgeWebDriver(WebDriverBase):

    def __init__(self, binfo=None):

        WebDriverBase.__init__(self, browserinfo=binfo)

    def WebDriver(self, path):

        self.driver = Edge(executable_path=path)
        return self.driver

class WebDriverConfig(WebDriverUtils):

    def __init__(self):

        WebDriverUtils.__init__(self)
        self.BROWSERS_LIST = \
        [
            {'browser_name':'firefox', 'url':'https://github.com/mozilla/geckodriver/releases', 'instance': FirefoxWebDriver},
            {'browser_name':'chrome', 'url':'https://chromedriver.chromium.org/downloads', 'instance': ChromeWebDriver},
            {'browser_name':'msedge', 'url':'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/', 'instance': EdgeWebDriver}
        ]

    # Obtem informarções do navegador atual e retorna uma instancia do webdriver
    def __GetCurrentBrowser(self):

        try:
            currentbrowser = self.GetBrowserInfo()
        except GetBrowserInfoException:
            raise GetBrowserInfoException
        else:
            for item in self.BROWSERS_LIST:
                if item['browser_name'] == currentbrowser['name']:
                    currentbrowser['url_download'] = item['url']
                    instance = item['instance']
                    return instance(binfo=currentbrowser)      
            return None

    def __SetWebdriverInfo(self, path , browser_name):

        with open(self.DEFAULT_PATH + self.CONFIG_FILE_NAME, 'w') as jsonfile:
            jsonobj = {'webdriver':path , 'browser':browser_name}
            dump(jsonobj , jsonfile , indent=4)

    # Caso o webdriver seja configurado com sucesso no arquivo config.json, 
    # retorna o caminho do webdriver e o nome do navegador
    def GetWebdriverInfo(self):

        try:
            with open(self.DEFAULT_PATH + self.CONFIG_FILE_NAME, 'r') as file:
                config = load(file)
        except FileNotFoundError:
            raise FileNotFoundError
        else:
            return config

    def SetWebdriverConfig(self):

        try:
            browser = self.__GetCurrentBrowser()

            if browser == None:
                print('[INFO] A versão atual não tem suporte para o navegador padrão')
                return False

            response_code, webdriver_name = browser.DownloadWebDriver(self.WEBDRIVER_PATH)
            if response_code == 200:
                full_path = self.ExtractFile(self.WEBDRIVER_PATH + webdriver_name)
                self.__SetWebdriverInfo(full_path, browser.name)
                return (browser, full_path)

            return False

        except GetBrowserInfoException:
            print('[ERRO] Não foi possivel identificar o navegador padrão', file=stderr)
            return False

    def Start(self, browser_name):
        
        for browser in self.BROWSERS_LIST:
            if browser['browser_name'] == browser_name:
                instance = browser['instance']
                return instance()

        return None