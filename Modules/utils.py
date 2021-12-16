from sys import platform, stderr
from os.path import basename
from os import getenv
from subprocess import CalledProcessError, check_output
from re import findall
from pathlib import Path
from json import dump
from zipfile import ZipFile
from tarfile import is_tarfile, open as tar_open

class GetBrowserInfoException(Exception):
    def __init__(self):
        super().__init__()

class WebDriverUtils:

    def __init__(self):

        if platform == 'linux' or platform == 'linux2':
            self.DEFAULT_PATH = getenv('HOME') + '/.ibot/'
        elif platform == 'win32':
            self.DEFAULT_PATH = getenv('USERPROFILE') + '/ibot/'

        self.WEBDRIVER_PATH = self.DEFAULT_PATH + 'webdriver/'
        self.CONFIG_FILE_NAME = 'config.json'

    def __GetDefaultBrowser(self):

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
                return {'path':browser_path , 'name':browser_name , 'os':platform}

    def __GetBrowserVersion(self,Browser):

        if platform == 'linux' or platform == 'linux2':
            browser_info = Browser.split(' ')
            return {'name':browser_info[1].lower(), 'version':browser_info[2] , 'os':platform}
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

    def GetBrowserInfo(self):

        defaultbrowser = self.__GetDefaultBrowser()
        if defaultbrowser == None:
            raise GetBrowserInfoException    

        browserinfo = self.__GetBrowserVersion(defaultbrowser)
        if browserinfo == None:
            raise GetBrowserInfoException

        return browserinfo

    def CreateDefaultPath(self):

        path = Path(self.WEBDRIVER_PATH)
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            return False
        else:
            with open(self.DEFAULT_PATH + self.CONFIG_FILE_NAME, 'w') as jsonfile:
                jsonobj = {'webdriver':'null'}
                dump(jsonobj , jsonfile)
            return True

    def ExtractFile(self,filename):
        
        if is_tarfile(filename):
            with tar_open(filename) as file:
                for member in file.getnames():
                    full_path = self.WEBDRIVER_PATH + member
                    file.extractall(path=self.WEBDRIVER_PATH)
        else:
            with ZipFile(filename) as file:
                if 'edgedriver' in filename: # Implementado o uso do webdriver edge apenas no windows
                    for member in file.namelist():
                        if '.exe' in member:
                            full_path = self.WEBDRIVER_PATH + member
                            file.extract(member , path=self.WEBDRIVER_PATH)
                            break
                else:
                    for member in file.namelist():
                        full_path = self.WEBDRIVER_PATH + member
                        file.extract(member , path=self.WEBDRIVER_PATH)
        return full_path