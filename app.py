from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import config
import win32print

app = Flask(__name__)

url = config.BASE_URL


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/management/about")
def get_info():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/management/printers", methods=["GET"])
def get_printers():
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


# @app.route("/management/printers/<int:printer_id>", methods=["POST"])
# def get_printers():
#     return jsonify(), 500


@app.route("/management/api")
def get_api():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/management/version")
def get_version():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
