from Modules.browser import WebDriverConfig
from Modules.instagram import Instagram

CHECK_MARK = u'\u2713'

def StartBrowser():

    try:
        webdriverconfig = WebDriverConfig()
        webdriverinfo = webdriverconfig.GetWebdriverInfo()
    except FileNotFoundError:
        print('[INFO] Não foi possivel encontrar o arquivo de configuração: {0}{1}'.format(webdriverconfig.DEFAULT_PATH,webdriverconfig.CONFIG_FILE_NAME))
        print('[...] Criando diretorios e arquivos padrão')
        status = webdriverconfig.CreateDefaultPath()
        if status:
            print('[ {} ] Diretorios e arquivos criados com sucesso'.format(CHECK_MARK))
            print('[...] Configurando webdriver')
            status = webdriverconfig.SetWebdriverConfig()
            if status == False:
                print('[INFO] Informe manualmente o caminho até o webdriver no arquivo: {0}{1}'.format(webdriverconfig.DEFAULT_PATH,webdriverconfig.CONFIG_FILE_NAME))
                exit(1)
            
            browser_instance = status[0]
            browser_instance_path = status[1]
            print('[ {0} ] Webdriver configurado com sucesso: {1} | Navegador: {2}'.format(CHECK_MARK,browser_instance_path , browser_instance.name))
            return (browser_instance, browser_instance_path)
    else: 
        if webdriverinfo['webdriver'] == 'null':
            print('[INFO] Nenhum webdriver configurado')
            print('[INFO] Informe manualmente o caminho até o webdriver no arquivo: {0}{1}'.format(webdriverconfig.DEFAULT_PATH,webdriverconfig.CONFIG_FILE_NAME))
            exit(1)
        else:
            browser_instance = webdriverconfig.Start(webdriverinfo['browser'])
            if browser_instance == None:
                print('[INFO] A versão atual não tem suporte para o navegador: {}'.format(webdriverinfo['browser']))
                exit(1)
                
            print('[ {0} ] Webdriver: {1} | Navegador: {2}'.format(CHECK_MARK,webdriverinfo['webdriver'], webdriverinfo['browser']))
            return (browser_instance, webdriverinfo['webdriver'])

if __name__ == '__main__':
    
    print('[...] Iniciando webdriver')
    browser, browser_path = StartBrowser()
    driver = browser.WebDriver(browser_path)
    driver.get('https://www.google.com')