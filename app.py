import json
import os
import requests
import win32api
from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
import config
import logger as R
from printer_config import printers_config

R.Logger("logs")

app = Flask(__name__)
# Configura Swagger para la documentacion de la API
swagger = Swagger(app)


# Ruta principal que carga la pagina de inicio con configuracion dinamica
@app.route("/")
def home():
    R.info("Cargando pagina inicial")
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
    R.info("Cargando informacion")
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
        R.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para obtener las impresoras disponibles en el sistema
@app.route("/printers", methods=["GET"])
def get_printers():
    R.info("Obteniendo impresoras del cliente")
    try:
        # Abre el archivo de configuración y lee las impresoras
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)

        # Devuelve la lista de impresoras en formato JSON
        if not printers_info:
            raise ValueError("No se encontraron impresoras en la configuración.")

        return jsonify(printers_info)
    except Exception as e:
        R.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para cargar la pagina de impresion con las impresoras disponibles
@app.route("/management/print")
def printers():
    R.info("Cargando pagina de impresion")
    try:
        # Lee la configuración de las impresoras desde config.json
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)
        return render_template("print.html", printers=printers_info)
    except Exception as e:
        R.error(f"Error al obtener impresoras: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/settings", methods=["POST"])
def save_settings():
    try:
        # Obtiene los valores enviados por el formulario
        printer_name = request.form.get("printer")
        copies = int(request.form.get("copies"))
        sides = request.form.get("sides")

        # Lee la configuración de las impresoras
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)

        # Encuentra la impresora seleccionada y actualiza la configuración
        for printer in printers_info:
            if printer["name"] == printer_name:
                printer["copies"] = copies
                printer["sides"] = int(sides)
                
        # Guarda la configuración actualizada
        with open(config.CONFIG_PATH, "w") as archive:
            json.dump(printers_info, archive, indent=1)

        return jsonify({"message": f"Ajustes guardados correctamente para {printer_name}."}), 200

    except Exception as e:
        R.error(f"Error al guardar configuración: {str(e)}")
        return render_template("alert.html", message=f"Error: {str(e)}")


# Ruta para cargar las versiones del sistema desde la configuracion
@app.route("/management/versions")
def get_versions():
    R.info("Cargando informacion de las versiones")
    try:
        # Obtiene las versiones desde la configuracion y las pasa a la plantilla
        return render_template("version.html", versions=config.CHANGES["versions"])
    except Exception as e:
        R.error(f"Error al cargar versiones: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para recibir el archivo a imprimir y enviarlo a la impresora
@app.route("/printers/<printer_id>", methods=["POST"])
def print_document(printer_id):
    try:
        # Obtiene el archivo y el numero de copias desde la solicitud
        file = request.files["file"]
        copies = int(request.form.get("copies"))

        try:
            # Guarda el archivo en una carpeta temporal
            file_path = os.path.join(temp_folder, file.filename)
            file.save(file_path)
        except Exception as e:
            return jsonify({"error": f"Error al guardar el archivo: {str(e)}"}), 500

        # Verifica que el archivo se haya guardado correctamente
        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 400

        # Imprime el archivo la cantidad de veces indicada
        for i in range(copies):
            win32api.ShellExecute(0, "print", file_path, printer_id, ".", 0)

        return jsonify({"message": "Documento enviado a imprimir"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para mostrar la documentacion de la API
@app.route("/management/docs")
def get_api():
    R.info("Cargando API")
    return render_template("api-doc.html")


# Ruta para mostrar los ajustes de la impresora
@app.route("/settings")
def get_settings():
    R.info("Cargando ajustes")
    try:
        # Lee las impresoras desde el archivo de configuración
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)

        # Pasa las impresoras al template
        return render_template("printerSettings.html", printers=printers_info)

    except Exception as e:
        R.error(f"Error al cargar los ajustes: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para mostrar las librerias, sus licencias y los derechos de autor
@app.route("/licenses")
def get_licenses():
    R.info("Cargando licencias")
    return render_template("licenses.html")


# Crea la carpeta temporal para guardar los archivos si no existe
temp_folder = "temp_folder"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# Llamar a la función para que se ejecute al inicio
printers_config()

if __name__ == "__main__":
    app.run()
