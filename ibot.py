from Modules.browser import WebDriverConfig

CHECK_MARK = u'\u2713'

print('[...] Obtendo configurações do webdriver')
try:
    webdriverconfig = WebDriverConfig()
    webdriverinfo = webdriverconfig.GetWebdriverConfig()
except FileNotFoundError:
    print('[INFO] Não foi possivel encontrar o arquivo de configuração: {0}{1}'.format(webdriverconfig.DEFAULT_PATH,webdriverconfig.CONFIG_FILE_NAME))
    print('[...] Criando diretorios e arquivos padrão...')
    status = webdriverconfig.CreateDefaultPath()
    if status:
        print('[ {} ] Diretorios e arquivos criados com sucesso'.format(CHECK_MARK))
        print('[...] Configurando webdriver')
        status = webdriverconfig.SetWebdriverConfig()
        if status == False:
            print('[INFO] Informe manualmente o caminho até o webdriver no arquivo: {0}{1}'.format(webdriverconfig.DEFAULT_PATH,webdriverconfig.CONFIG_FILE_NAME))
            exit(1)
        elif status[0]:
            webdriverinfo = status[1]
            print('[ {0} ] Webdriver configurado com sucesso: {1} | Navegador: {2}'.format(CHECK_MARK,webdriverinfo['webdriver'] , webdriverinfo['browser']))
else: 
    if webdriverinfo['webdriver'] == 'null':
        print('[INFO] Nenhum webdriver configurado')
        print('[INFO] Informe manualmente o caminho até o webdriver no arquivo: {0}{1}'.format(webdriverconfig.DEFAULT_PATH,webdriverconfig.CONFIG_FILE_NAME))
        exit(1)
    else:
        print('[ {0} ] Webdriver encontrado: {1} | Navegador: {2}'.format(CHECK_MARK,webdriverinfo['webdriver'], webdriverinfo['browser']))