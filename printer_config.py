import json
import os
import win32print
import config
import logger as R


# Función para obtener la configuración de la impresora
def get_printer_config(printer):
    try:
        # Obtiene la información de la impresora
        printer_handle = win32print.OpenPrinter(printer)
        printer_info = win32print.GetPrinter(printer_handle, 2)
        dev_mode = printer_info.get("pDevMode", None)
        duplex = (
            dev_mode.Duplex > 1 if dev_mode and hasattr(dev_mode, "Duplex") else False
        )
        win32print.ClosePrinter(printer_handle)
        return {
            "name": printer,
            "duplex": duplex,
            "copies": 1,
            "format": "pdf",
            "sides": 1,
        }
    except Exception as e:
        R.error(f"Error al obtener información de la impresora {printer}: {str(e)}")
        return {
            "name": printer,
            "duplex": False,
            "copies": 1,
            "format": "pdf",
            "sides": 1,
        }


# Función para verificar y reparar campos faltantes en la configuración de las impresoras
def fix_missing_fields(printer_config):
    # Valores predeterminados para los campos que faltan
    defaults = {"duplex": False, "copies": 1, "format": "pdf", "sides": 1}

    # Reemplaza los campos faltantes por los valores predeterminados
    for field, default_value in defaults.items():
        if field not in printer_config:
            printer_config[field] = default_value

    return printer_config


# Función que configura las impresoras (crea el archivo si no existe)
def printers_config():
    R.info("------------------------------------------Iniciando programa------------------------------------------")
    printers_info = []

    # Verifica si el archivo de configuración existe y si está vacío
    if os.path.exists(config.CONFIG_PATH):
        with open(config.CONFIG_PATH, "r") as archive:
            # Verifica si el archivo está vacío
            if os.stat(config.CONFIG_PATH).st_size == 0:
                printers_info = (
                    []
                )  # Si el archivo está vacío, inicializa una lista vacía
                R.warning(
                    f"El archivo {config.CONFIG_PATH} está vacío. Inicializando configuración vacía."
                )
            else:
                printers_info = json.load(archive)
                R.info(
                    f"El archivo {config.CONFIG_PATH} ya existe. Verificando nuevas impresoras."
                )
    else:
        R.info(
            f"Archivo {config.CONFIG_PATH} no existe. Creando archivo de configuración."
        )

    # Obtiene las impresoras del sistema
    printer_names = [printer[2] for printer in win32print.EnumPrinters(2)]

    # Recorre las impresoras y añade las nuevas
    existing_printers = {printer["name"] for printer in printers_info}
    for printer in printer_names:
        if printer not in existing_printers:
            printer_config = get_printer_config(printer)
            printers_info.append(printer_config)
            R.info(
                f"Impresora nueva encontrada: {printer}. Se añadió al archivo de configuración."
            )

    # Repara campos faltantes en las configuraciones de las impresoras
    for printer in printers_info:
        updated_config = fix_missing_fields(printer)
        # Actualiza la configuración de la impresora si faltaba algún campo
        printer.update(updated_config)

    # Guarda la configuración (creada o actualizada)
    with open(config.CONFIG_PATH, "w") as archive:
        json.dump(printers_info, archive, indent=4)
        R.info(f"Archivo de configuración {config.CONFIG_PATH} actualizado.")
