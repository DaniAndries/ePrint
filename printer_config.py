import json
import os
import win32print
import win32ui
import config
import logger as D


# Funcion que configura las impresoras (crea el archivo si no existe)
def printers_config():
    D.info(
        "------------------------------------------Iniciando programa------------------------------------------"
    )
    printers_info = []

    # Verifica si el archivo de configuracion existe y si esta vacio
    if os.path.exists(config.CONFIG_PATH):
        with open(config.CONFIG_PATH, "r") as archive:
            if os.stat(config.CONFIG_PATH).st_size == 0:
                printers_info = []
                D.warning(
                    f"El archivo {config.CONFIG_PATH} está vacío. Inicializando configuración vacía."
                )
            else:
                printers_info = json.load(archive)
                D.info(
                    f"El archivo {config.CONFIG_PATH} ya existe. Verificando nuevas impresoras."
                )
    else:
        D.info(
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
            D.info(
                f"Impresora nueva encontrada: {printer}. Se añadió al archivo de configuración."
            )

    # Repara campos faltantes (incluyendo el DPI, solo si es necesario)
    for printer in printers_info:
        # Actualiza el DPI solo si falta en la configuracion
        get_printer_dpi(printer)
        # Repara otros campos faltantes
        fix_missing_fields(printer)

    # Guarda la configuracion (creada o actualizada)
    with open(config.CONFIG_PATH, "w") as archive:
        json.dump(printers_info, archive, indent=4)
        D.info(f"Archivo de configuración {config.CONFIG_PATH} actualizado.")


# Funcion para obtener la configuracion inicial de la impresora
def get_printer_config(printer):
    try:
        attributes = get_printer_attributes(printer)
        return {
            "name": printer,
            "duplex": attributes["duplex"],
            "copies": 1,
            "sides": 1,
            "dpi": attributes["dpi"],
            "max_dpi": attributes["dpi"],
        }
    except Exception as e:
        D.error(f"Error al obtener información de la impresora {printer}: {str(e)}")
        return {
            "name": printer,
            "duplex": False,
            "copies": 1,
            "sides": 1,
            "dpi": attributes["dpi"],
            "max_dpi": attributes["dpi"],
        }


# Funcion para verificar y reparar campos faltantes en la configuracion
def fix_missing_fields(printer_config):
    # Si falta el campo 'duplex', lo actualiza usando get_printer_attributes
    if "duplex" not in printer_config:
        attributes = get_printer_attributes(printer_config["name"])
        printer_config["duplex"] = attributes["duplex"]
    # Si faltan 'copies' o 'sides', se asigna el valor por defecto 1
    if "copies" not in printer_config:
        printer_config["copies"] = 1
    if "sides" not in printer_config:
        printer_config["sides"] = 1
    # El DPI ya se actualiza con get_printer_dpi si falta
    return printer_config


# Funcion para obtener los atributos basicos de la impresora: DPI y duplex.
def get_printer_attributes(printer):
    try:
        dpi = get_printer_dpi({"name": printer})

        printer_handle = win32print.OpenPrinter(printer)
        printer_info = win32print.GetPrinter(printer_handle, 2)
        dev_mode = printer_info.get("pDevMode", None)
        duplex = (
            dev_mode.Duplex > 1 if dev_mode and hasattr(dev_mode, "Duplex") else False
        )
        win32print.ClosePrinter(printer_handle)

        return {"dpi": dpi, "duplex": duplex}
    except Exception as e:
        D.error(f"Error al obtener atributos de la impresora {printer}: {str(e)}")
        return {"dpi": 200, "duplex": False}


# Funcion que obtiene el DPI, pero solo se ejecuta si el campo "dpi" no esta definido o es falsy.
def get_printer_dpi(printer_config):
    if not printer_config.get("dpi"):
        try:
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_config["name"])
            horizontal_dpi = hDC.GetDeviceCaps(88)
            vertical_dpi = hDC.GetDeviceCaps(90)
            dpi = (
                horizontal_dpi
                if horizontal_dpi == vertical_dpi
                else min(horizontal_dpi, vertical_dpi)
            )
            printer_config["dpi"] = dpi
            D.info(f"DPI obtenido para {printer_config['name']}: {dpi}")
        except Exception as e:
            D.error(f"Error al obtener DPI para {printer_config['name']}: {str(e)}")
            printer_config["dpi"] = 200  # Valor por defecto en caso de error
    return printer_config["dpi"]
