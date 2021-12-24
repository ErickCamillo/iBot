from sys import stderr
from requests import Session
from bs4 import BeautifulSoup
from re import search
from json import load, dump
from os.path import basename
from selenium.webdriver import Firefox , Chrome, Edge
from Modules.utils import  WebDriverUtils ,GetBrowserInfoException

BROWSERS_LIST = \
[
    {'browser_name':'firefox', 'download_link':'https://github.com/mozilla/geckodriver/releases'},
    {'browser_name':'chrome', 'download_link':'https://chromedriver.chromium.org/downloads'},
    {'browser_name':'msedge', 'download_link':'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/'}
]

class WebDriverConfig(WebDriverUtils):

    def __init__(self):
        WebDriverUtils.__init__(self)

    # Verifica se o navegador padrão esta na lista de navegadores que são suportados.
    def __VerifyCurrentBrowser(self):

        try:
            currentbrowser = self.GetBrowserInfo()
        except GetBrowserInfoException:
            return GetBrowserInfoException
        else:
            for browser in BROWSERS_LIST:
                if browser['browser_name'] == currentbrowser['name']:
                    currentbrowser['link'] = browser['download_link']
                    return currentbrowser       
            return None

    # Retorna o link de download e nome do webdriver
    def __PageParser(self, browser_info , page):

        if browser_info['name'] == 'firefox':
            box = page.find('div', class_='Box-body')
            webdriver_version = box.find('a', class_='Link--primary').text

            if browser_info['os'] == 'win32':
                webdriver_title = 'geckodriver-v{}-win64.zip'.format(webdriver_version)
            elif browser_info['os'] == 'linux' or 'linux2':
                webdriver_title = 'geckodriver-v{}-linux64.tar.gz'.format(webdriver_version)

            for li in page.find_all('li', class_='Box-row'):
                if li.a.span.get_text() == webdriver_title:
                    url_download = search(r'(\w+.//\w+.\w+)',browser_info['link']).group() + li.a['href']
                    return (webdriver_title , url_download)
        
        elif browser_info['name'] == 'chrome':
            if browser_info['os'] == 'win32':
                webdriver_title = 'chromedriver_win32.zip'
            elif browser_info['os'] == 'linux' or browser_info['os'] == 'linux2':
                webdriver_title = 'chromedriver_linux64.zip'

            spans = page.find_all('span', class_='aw5Odc')
            for span in spans:
                webdriver_version = span.a.text.split(' ')[1]
                webdriver_version_firstnumber = search(r'([0-9])+', webdriver_version).group(0)
                browser_version_firstnumber = search(r'([0-9])+', browser_info['version']).group(0)
                if browser_version_firstnumber == webdriver_version_firstnumber:
                    url_download = span.a['href'] + webdriver_title
                    url_download = url_download.replace('index.html?path=', '')
                    return (webdriver_title , url_download)
        
        # Implementado o uso do webdriver edge apenas no windows
        elif browser_info['name'] == 'msedge':
            elements_p = page.find_all('p', class_='driver-download__meta')
            for p in elements_p:
                webdriver_version = p.text
                webdriver_version_firstnumber = search(r'([0-9])+', webdriver_version).group(0)
                browser_version_firstnumber = search(r'([0-9])+', browser_info['version']).group(0)
                if browser_version_firstnumber == webdriver_version_firstnumber:
                    for a in p.find_all('a'):
                        if a.text == 'x64':
                            url_download = a['href']
                            webdriver_title = basename(url_download)
                            return (webdriver_title , url_download)
                    
    def __DownloadWebDriver(self, browser_info):

        request = Session()
        response = request.get(browser_info['link'])
        if response.status_code != 200:
            print('[ERRO] Não foi possivel acessar a pagina de download do webdriver: {0}:{1}'
            .format(browser_info['name'] , browser_info['link']), file=stderr)
            return (response.status_code, None)

        page = BeautifulSoup(response.text , 'html.parser')

        webdriver_name , url_download = self.__PageParser(browser_info , page)
        driver = request.get(url_download)
        if driver.status_code != 200:
            print('[ERRO] Não foi possivel fazer o download do webdriver: {}'.format(webdriver_name), file=stderr)
            return (driver.status_code,None)
        with open(self.WEBDRIVER_PATH + webdriver_name , 'wb') as file:
            file.write(driver.content)

        return (200, webdriver_name)

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

        browserinfo = self.__VerifyCurrentBrowser()
        if browserinfo == GetBrowserInfoException:
            print('[ERRO] Não foi possivel identificar o navegador padrão', file=stderr)
            return False
        elif browserinfo == None:
            print('[INFO] A versão atual não tem suporte para fazer a configuração automatica de acordo com o navegador padrão')
            return False
        else:
            response_code, webdriver_name = self.__DownloadWebDriver(browserinfo)
            if response_code != 200:
                return False
            else:
                full_path = self.ExtractFile(self.WEBDRIVER_PATH + webdriver_name)
                self.__SetWebdriverInfo(full_path, browserinfo['name'])
                return (True, {'webdriver':full_path , 'browser':browserinfo['name']})

    # Cria uma instancia do webdriver de acordo com o webdriver configurado
    # No arquivo DEFAULT_PATH/config.json
    def WebDriver(self, wdinfo):
       
        webdrivers = [{'name':'firefox','instance':Firefox},
                     {'name':'chrome', 'instance':Chrome},
                     {'name':'msedge', 'instance':Edge}]

        for webdriver in webdrivers:
            if webdriver['name'] == wdinfo['browser'].lower():
                driver = webdriver['instance']
                return driver(executable_path=wdinfo['webdriver'])
        
        return None

# Usando a maior quantidade de tecnicas para não ser detectado como bot
class UndectableMode:
    pass