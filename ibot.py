from Modules.browser import SetWebdriverConfig, GetWebdriverPath
from Modules.utils import CreateDefaultPath, CONFIG_FILE_NAME

print('[INFO] Obtendo caminho até o webdriver...')
webdriverpath = GetWebdriverPath()
if webdriverpath == FileNotFoundError:
    print('[INFO] Não foi possivel encontrar o arquivo de configuração: {}'.format(CONFIG_FILE_NAME))
    print('[INFO] Criando diretorios e arquivos padrão...')
    status = CreateDefaultPath()
    if status:
        print('[INFO] Diretorios e arquivos criado com sucesso')
        print('[INFO] Configurando webdriver...')
        status = SetWebdriverConfig()
        if status == False:
            print('[INFO] Informe manualmente o caminho até o webdriver no arquivo: {}'.format(CONFIG_FILE_NAME))
            exit(1)
        print('[INFO] Webdriver configurado com sucesso')
elif webdriverpath == 'null':
    print('[INFO] Nenhum caminho informado para o webdriver')