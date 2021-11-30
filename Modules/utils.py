from sys import platform, stderr
from os.path import basename
from subprocess import CalledProcessError, check_output
from re import findall

class GetBrowserInfoException(Exception):
    def __init__(self):
        super().__init__()

def __GetDefaultBrowser():

    if platform == 'linux' or platform == 'linux2':
        try:
            output = check_output(['x-www-browser', '--version'])
        except CalledProcessError as error:
            print('[ERRO] Ocorreu um erro enquanto executava o navegador padrão', file=stderr)
            print('Comando: {}'.format(error.cmd))
            return None
        except FileNotFoundError as error:
            print('[ERRO] Não foi possivel executar o alias "x-www-browser"', file=stderr)
            print('[Código {1}]: {0}'.format(error.strerror, error.errno))
            return None
        else:
            return output.decode('utf-8')
    elif platform == 'win32': 
        from winreg import HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, OpenKey, QueryValueEx
        try:
            # Obtendo o ID do navegador escolhido pelo usuario
            with OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice') as regkey:
                browser_id = QueryValueEx(regkey, 'ProgId')[0]

            # Obtendo o caminho completo até o executavel do navegador
            with OpenKey(HKEY_CLASSES_ROOT, r'{0}\shell\open\command'.format(browser_id)) as regkey:
                browser_path = QueryValueEx(regkey, None)[0].split('"')[1]
        except OSError as error:
            print('[INFO] Não foi possivel ler as chaves de registro do navegador padrão', file=stderr)
            print('[ERRO] OpenKey/QueryValueEx: {0}'.format(error.strerror) , file=stderr)
            return None
        else:
            browser_name = basename(browser_path).split('.')[0]
            return {'id':browser_id , 'path':browser_path , 'name':browser_name}

def __GetBrowserVersion(Browser):

    if platform == 'linux' or platform == 'linux2':
        browser_info = Browser.split(' ')
        return {'name':browser_info[1], 'version':browser_info[2]}
    elif platform == 'win32':
        try:
            # Obtendo a versão do browser padrão, via linha de comando
            output = check_output(['powershell', '-c' , "(Get-Item '{0}').VersionInfo".format(Browser['path'])])
        except CalledProcessError as error:
            print('[ERRO] Ocorreu um erro enquanto executava o comando para obter a versão do navegador', file=stderr)
            print('Comando: {0}'.format(error.cmd), file=stderr)
            return None
        except FileNotFoundError as error:
            print('[ERRO] Não foi possivel executar o powershell para obter a versão do navegador', file=stderr)
            print('[Código {1}]: {0}'.format(error.strerror, error.errno), file=stderr)
            return None
        else:
            # Extraindo a versão
            version = findall(r'([0-9].*[0-9])',output.decode('utf-8').strip())
            Browser['version'] = version[0].split(' ')[0] 
            return Browser

def GetBrowserInfo():

    defaultbrowser = __GetDefaultBrowser()
    if defaultbrowser == None:
        raise GetBrowserInfoException    

    browserinfo = __GetBrowserVersion(defaultbrowser)
    if browserinfo == None:
        raise GetBrowserInfoException

    return browserinfo