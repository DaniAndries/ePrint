import json
import os
import time
import requests
import win32api
import win32print
from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
import config
import logger as D
from printer_config import printers_config

D.Logger("logs")

app = Flask(__name__)
# Configura Swagger para la documentacion de la API
swagger = Swagger(app)


# Ruta principal que carga la pagina de inicio con configuracion dinamica
@app.route("/")
def home():
    D.info("Cargando pagina inicial")
    return render_template(
        "about.html",
        LOGS=config.LOGS,
        PATH=config.PATH,
        PLATFORM=config.PLATFORM,
        VERSION=config.VERSION,
    )


# Ruta para obtener informacion sobre la plataforma
@app.route("/management/about")
def get_info():
    D.info("Cargando informacion")
    try:
        response = requests.get(config.BASE_URL)
        response.raise_for_status()
        return render_template(
            "about.html",
            LOGS=config.LOGS,
            PATH=config.PATH,
            PLATFORM=config.PLATFORM,
            VERSION=config.VERSION,
        )
    except requests.exceptions.RequestException as e:
        D.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para cargar la pagina de impresion con las impresoras disponibles
@app.route("/management/print")
def printers():
    D.info("Cargando pagina de impresion")
    try:
        # Lee la configuración de las impresoras desde config.json
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)
        return render_template("print.html", printers=printers_info)
    except Exception as e:
        D.error(f"Error al obtener impresoras: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para cargar las versiones del sistema desde la configuracion
@app.route("/management/versions")
def get_versions():
    D.info("Cargando informacion de las versiones")
    try:
        # Obtiene las versiones desde la configuracion y las pasa a la plantilla
        return render_template("version.html", versions=config.CHANGES["versions"])
    except Exception as e:
        D.error(f"Error al cargar versiones: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para mostrar la documentacion de la API
@app.route("/management/docs")
def get_api():
    D.info("Cargando API")
    return render_template("api-doc.html")


# Ruta para obtener las impresoras disponibles en el sistema
@app.route("/printers", methods=["GET"])
def get_printers():
    D.info("Obteniendo impresoras del cliente")
    try:
        # Abre el archivo de configuración y lee las impresoras
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)

        # Devuelve la lista de impresoras en formato JSON
        if not printers_info:
            raise ValueError("No se encontraron impresoras en la configuración.")

        return jsonify(printers_info)
    except Exception as e:
        D.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/printers/<printer_id>", methods=["POST"])
def print_document(printer_id):
    try:
        hprinter = win32print.OpenPrinter(printer_id)

        # Obtiene el archivo y el numero de copias desde la solicitud
        file = request.files["file"]
        copies = int(
            request.form.get("copies", 1)
        )  # Valor predeterminado de 1 copia si no se especifica

        # Guarda el archivo en la carpeta temporal
        temp_folder = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_folder, exist_ok=True)
        file_path = os.path.join(temp_folder, file.filename)
        file.save(file_path)

        # Verifica que el archivo se haya guardado correctamente
        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 400

        # Determina la extension del archivo para procesarlo adecuadamente
        file_extension = file.filename.rsplit(".", 1)[-1].lower()

        if file_extension == "zpl":
            # Imprime el archivo ZPL la cantidad de veces indicada
            for _ in range(copies):
                win32api.ShellExecute(
                    0, "print", file_path, f'/d:"{printer_id}"', ".", 0
                )
        elif file_extension == "pdf":
            with open(file_path, "rb") as f:
                data = f.read()
                # Imprime el archivo PDF la cantidad de veces indicada
                for _ in range(copies):
                    try:
                        # Empieza un trabajo de impresion con el nombre del archivo
                        job_info = (
                            file.filename,
                            None,
                            "RAW",
                        )  # Usa el nombre real del archivo
                        win32print.StartDocPrinter(hprinter, 1, job_info)

                        try:
                            win32print.StartPagePrinter(hprinter)
                            win32print.WritePrinter(
                                hprinter, data
                            )  # Envia los datos a la impresora

                            win32print.EndPagePrinter(hprinter)
                        finally:
                            win32print.EndDocPrinter(hprinter)
                    except Exception as e:
                        print(f"Error al imprimir PDF: {e}")
        else:
            return jsonify({"error": "Formato de archivo no soportado"}), 400

        return jsonify({"message": "Documento enviado a imprimir"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para configurar la impresora
@app.route("/management/settings", methods=["POST"])
def save_settings():
    try:
        print(f"Content-Type recibido: {request.content_type}")
        # Obtiene los datos enviados como JSON
        data = request.get_json()

        # Obtiene los valores del JSON
        printer_name = data.get("printer")
        copies = int(data.get("copies"))
        sides = data.get("sides")
        dpi = data.get("dpi")  # Si también necesitas dpi

        # Lee la configuracion de las impresoras
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)

        # Encuentra la impresora seleccionada y actualiza la configuracion
        for printer in printers_info:
            if printer["name"] == printer_name:
                printer["copies"] = copies
                printer["sides"] = int(sides)
                if printer["max_dpi"] > int(dpi):
                    printer["dpi"] = dpi
                else:
                    printer["dpi"] = printer["max_dpi"]
                    D.Logger(
                        f"El DPI seleccionado es mayor al máximo permitido, se ajustó a {printer['max_dpi']}"
                    )

        # Guarda la configuracion actualizada
        with open(config.CONFIG_PATH, "w") as archive:
            json.dump(printers_info, archive, indent=1)

        return (
            jsonify(
                {"message": f"Ajustes guardados correctamente para {printer_name}."}
            ),
            200,
        )

    except Exception as e:
        D.error(f"Error al guardar configuración: {str(e)}")
        return (
            jsonify({"error": f"Error: {str(e)}"}),
            500,
        )


# Ruta para mostrar los ajustes de la impresora
@app.route("/management/settings")
def get_settings():
    D.info("Cargando ajustes")
    try:
        # Lee las impresoras desde el archivo de configuracion
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)

        # Pasa las impresoras al template
        return render_template("printerSettings.html", printers=printers_info)

    except Exception as e:
        D.error(f"Error al cargar los ajustes: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para mostrar las librerias, sus licencias y los derechos de autor
@app.route("/management/licenses")
def get_licenses():
    D.info("Cargando licencias")
    return render_template("licenses.html")


# Crea la carpeta temporal para guardar los archivos si no existe
temp_folder = "temp_folder"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# Llamar a la funcion para que se ejecute al inicio
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    printers_config()

if __name__ == "__main__":
    app.run()
