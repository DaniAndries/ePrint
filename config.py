import getpass
import platform
import json

PORT = 19191
BASE_URL = f"http://127.0.0.1:{PORT}/"

# ---------------------------------------------------------------------------------
# -------------------------------Program    data-----------------------------------

VERSION = 1
PLATFORM = platform.system()
PATH = f"C:/Users/{getpass.getuser()}/AppData/Local/ePrint"
CONFIG_PATH = f"{PATH}/config.json"
LOGS = f"C:/Users/{getpass.getuser()}/AppData/Local/ePrint/Logs"

# ---------------------------------------------------------------------------------
# ---------------------------Configuracion Predeterminada--------------------------

# CONFIG = [{"nombre": "ePrint", "copies": 1, "format": "pdf", "duplex": 1}]

# ---------------------------------------------------------------------------------
# -------------------------------Notas de Version----------------------------------

with open("versions.json", "r") as f:
    CHANGES = json.load(f)
