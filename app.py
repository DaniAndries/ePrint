import os
import tempfile
import requests
import win32print
import win32api
from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
import config
import logger as R

# Inicializa el logger para registrar eventos importantes
R.Logger("logs")

# Crea la aplicacion Flask
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
        # Realiza una peticion a un endpoint remoto
        response = requests.get(config.BASE_URL)
        response.raise_for_status()  # Si hay un error en la respuesta, lanza una excepcion
        return render_template(
            "about.html",
            LOGS=config.LOGS,
            PATH=config.PATH,
            PLATFORM=config.PLATFORM,
            VERSION=config.VERSION,
        )
    except requests.exceptions.RequestException as e:
        # Maneja errores de peticiones HTTP
        R.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para obtener las impresoras disponibles en el sistema
@app.route("/printers", methods=["GET"])
def get_printers():
    R.info("Obteniendo impresoras del cliente")
    try:
        printers_info = []
        # Obtiene el nombre de todas las impresoras
        printer_names = [printer[2] for printer in win32print.EnumPrinters(2)]
        for printer in printer_names:
            try:
                # Abre cada impresora y obtiene su informacion
                printer_handle = win32print.OpenPrinter(printer)
                printer_info = win32print.GetPrinter(printer_handle, 2)
                dev_mode = printer_info.get("pDevMode", None)
                # Verifica si la impresora soporta duplex (impresion a dos caras)
                duplex = (
                    dev_mode.Duplex > 1
                    if dev_mode and hasattr(dev_mode, "Duplex")
                    else False
                )
                win32print.ClosePrinter(printer_handle)
            except Exception:
                duplex = False  # Si falla, se asume que no tiene soporte duplex
            printers_info.append({"name": printer, "duplex": duplex})
        return jsonify(printers_info)
    except Exception as e:
        # Maneja cualquier error al obtener las impresoras
        R.error(f"Error: {str(e)}")
        return jsonify([]), 500


# Ruta para cargar la pagina de impresion con las impresoras disponibles
@app.route("/management/print")
def printers():
    R.info("Cargando pagina de impresion")
    try:
        # Llama a la funcion para obtener las impresoras y las pasa a la plantilla
        printers_info = get_printers().json
        return render_template("print.html", printers=printers_info)
    except Exception as e:
        # Maneja el error si no se puede obtener la informacion de las impresoras
        R.error(f"Error al obtener impresoras: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para cargar las versiones del sistema desde la configuracion
@app.route("/management/versions")
def get_versions():
    R.info("Cargando informacion de las versiones")
    try:
        # Obtiene las versiones desde la configuracion y las pasa a la plantilla
        return render_template("version.html", versions=config.CHANGES["versions"])
    except Exception as e:
        # Maneja cualquier error al cargar la informacion de las versiones
        R.error(f"Error al cargar versiones: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Ruta para recibir el archivo a imprimir y enviarlo a la impresora
@app.route("/printers/<printer_id>", methods=["POST"])
def print_document(printer_id):
    try:
        # Obtiene el archivo y el numero de copias desde la solicitud
        file = request.files["format"]
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


# Crea la carpeta temporal para guardar los archivos si no existe
temp_folder = "temp_folder"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# Inicia la aplicacion Flask
if __name__ == "__main__":
    R.info("--------------------------Iniciando programa--------------------------")
    app.run()
