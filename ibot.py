from Modules.browser import SetWebdriverConfig
from Modules.utils import CreateDefaultPath, DEFAULT_PATH

print('[INFO] Verificando diretorios e arquivos necessarios...')
status = CreateDefaultPath()
if status == True:
    print('[INFO] Identificando e configurando navegador padrão...')
    browsersetting = SetWebdriverConfig()
    if(browsersetting == False):
        print('[INFO] Informe manualmente o webdriver no arquivo: {}config.json'.format(DEFAULT_PATH))
        exit(0)
else:
    print('[INFO] Webdriver ja esta configurado')
