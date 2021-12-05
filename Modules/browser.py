from sys import stderr
from requests import Session
from bs4 import BeautifulSoup
from utils import GetBrowserInfo, GetBrowserInfoException, DEFAULT_PATH, WEBDRIVER_PATH
from re import search

BROWSERS_LIST = \
[
    {'browser_name':'firefox', 'download_link':'https://github.com/mozilla/geckodriver/releases'},
    {'browser_name':'chrome', 'download_link':'https://chromedriver.chromium.org/downloads'},
    {'browser_name':'msedge', 'download_link':'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/'}
]

# Verifica se o navegador padrão esta na lista de navegadores que são suportados.
def __VerifyCurrentBrowser():

    try:
        currentbrowser = GetBrowserInfo()
    except GetBrowserInfoException:
        print('[INFO] Não foi possivel configurar automaticamente o webdriver', file=stderr)
        print('[INFO] Informe manualmente o webdriver no arquivo: {}webdriverconfig.json'.format(DEFAULT_PATH), file=stderr)
        return GetBrowserInfoException
    else:
        for browser in BROWSERS_LIST:
            if browser['browser_name'] == currentbrowser['name']:
                currentbrowser['link'] = browser['download_link']
                return currentbrowser       
        return None

def __DownloadWebDriver(browser_info):

    request = Session()
    response = request.get(browser_info['link'])
    if response.status_code != 200:
        print('[ERRO] Não foi possivel acessar a pagina de download do webdriver: {0}:{1}'
        .format(browser_info['name'] , browser_info['link']), file=stderr)
        return response.status_code

    page = BeautifulSoup(response.text , 'html.parser')

    if browser_info['name'] == 'firefox':
        box = page.find('div', class_='Box-body')
        webdriver_version = box.find('a', class_='Link--primary').text

        if browser_info['os'] == 'win32':
            webdriver_title = 'geckodriver-v{}-win64.zip'.format(webdriver_version)
        elif browser_info['os'] == 'linux' or 'linux2':
            webdriver_title = 'geckodriver-v{}-linux64.tar.gz'.format(webdriver_version)

        for li in page.find_all('li', class_='Box-row'):
            if li.a.span.get_text() == webdriver_title:
                link = search(r'(\w+.//\w+.\w+)',browser_info['link']).group() + li.a['href']
                driver = request.get(link)
                if driver.status_code != 200:
                    print('[ERRO] Não foi possivel fazer o download do webdriver: {}'.format(webdriver_title), file=stderr)
                    return driver.status_code
                with open(WEBDRIVER_PATH + webdriver_title , 'wb') as file:
                    file.write(driver.content)
                break
