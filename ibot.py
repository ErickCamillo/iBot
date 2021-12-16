from Modules.browser import WebDriverConfig

print('[INFO] Obtendo caminho até o webdriver...')
try:
    webdriverconfig = WebDriverConfig()
    webdriverpath = webdriverconfig.GetWebdriverPath()
except FileNotFoundError:
    print('[INFO] Não foi possivel encontrar o arquivo de configuração: {}'.format(webdriverconfig.CONFIG_FILE_NAME))
    print('[INFO] Criando diretorios e arquivos padrão...')
    status = webdriverconfig.CreateDefaultPath()
    if status:
        print('[INFO] Diretorios e arquivos criado com sucesso')
        print('[INFO] Configurando webdriver...')
        status = webdriverconfig.SetWebdriverConfig()
        if status == False:
            print('[INFO] Informe manualmente o caminho até o webdriver no arquivo: {}'.format(webdriverconfig.CONFIG_FILE_NAME))
            exit(1)
        print('[INFO] Webdriver configurado com sucesso')
else: 
    if webdriverpath == 'null':
        print('[INFO] Nenhum caminho informado para o webdriver')
    else:
        print('[INFO] Webdriver: {}'.format(webdriverpath))