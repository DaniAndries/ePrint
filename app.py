from platform import release
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


def get_printers():
    try:
        return [printer[2] for printer in win32print.EnumPrinters(2)]
    except Exception:
        return []


@app.route("/management/print")
def printers():
    printers = get_printers()
    return render_template("print.html", printers=printers)

@app.route("/management/api")
def get_api():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/management/versions")
def get_versions():
    try:
       
        return render_template("version.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
