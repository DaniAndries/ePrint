import getpass
import platform
import json

BASE_URL = "http://127.0.0.1:19191/"
PORT = 19191

#---------------------------------------------------------------------------------
#-------------------------------Program    data-----------------------------------

VERSION = 1
PLATFORM = platform.system()
PATH = f"C:/Users/{getpass.getuser()}/AppData/Local/ePrint"
LOGS = f"C:/Users/{getpass.getuser()}/AppData/Local/ePrint/Logs"

#---------------------------------------------------------------------------------
#-------------------------------Notas de Version----------------------------------

with open('versions.json', 'r') as f:
    CHANGES = json.load(f)