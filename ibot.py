from Modules.utils import *

try:
    binfo = GetBrowserInfo()
except GetBrowserInfoException:
    print('Não foi possivel idenficar o navegador.')
else:
    print('Navegador: {0}\nVersão: {1}'.format(binfo['name'], binfo['version']))
   
   
createDir()    
