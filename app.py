import os
import tempfile
import requests
import win32print
import win32api
from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
import config
import logger as R

R.Logger("logs")

app = Flask(__name__)
swagger = Swagger(app)


@app.route("/")
def home():
    R.info("Cargando página inicial")
    return render_template(
        "about.html",
        LOGS=config.LOGS,
        PATH=config.PATH,
        PLATFORM=config.PLATFORM,
        VERSION=config.VERSION,
    )


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


@app.route("/printers", methods=["GET"])
def get_printers():
    R.info("Obteniendo impresoras del cliente")
    try:
        printers_info = []
        printer_names = [printer[2] for printer in win32print.EnumPrinters(2)]
        for printer in printer_names:
            try:
                printer_handle = win32print.OpenPrinter(printer)
                printer_info = win32print.GetPrinter(printer_handle, 2)
                dev_mode = printer_info.get("pDevMode", None)
                duplex = (
                    dev_mode.Duplex > 1
                    if dev_mode and hasattr(dev_mode, "Duplex")
                    else False
                )
                win32print.ClosePrinter(printer_handle)
            except Exception:
                duplex = False
            printers_info.append({"name": printer, "duplex": duplex})
        return jsonify(printers_info)
    except Exception as e:
        R.error(f"Error: {str(e)}")
        return jsonify([]), 500


@app.route("/management/print")
def printers():
    R.info("Cargando página de impresión")
    try:
        printers_info = get_printers().json
        return render_template("print.html", printers=printers_info)
    except Exception as e:
        R.error(f"Error al obtener impresoras: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/management/versions")
def get_versions():
    R.info("Cargando información de las versiones")
    try:
        return render_template("version.html", versions=config.CHANGES["versions"])
    except Exception as e:
        R.error(f"Error al cargar versiones: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/printers/<printer_id>", methods=["POST"])
def print_document(printer_id):
    try:
        file = request.files["format"]
        copies = int(request.form.get("copies"))

        try:
            file_path = os.path.join(temp_folder, file.filename)
            file.save(file_path)
        except Exception as e:
            return jsonify({'error': f'Error al guardar el archivo: {str(e)}'}), 500

        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 400

        for i in range(copies):
            win32api.ShellExecute(0, "print", file_path, printer_id, ".", 0)
        
        return jsonify({"message": "Documento enviado a imprimir"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/management/docs")
def get_api():
    R.info("Cargando API")
    return render_template("api-doc.html")

temp_folder = "temp_folder"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

if __name__ == "__main__":
    R.info("--------------------------Iniciando programa--------------------------")
    app.run()
