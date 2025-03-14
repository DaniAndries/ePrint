# 🖨️ Aplicación de Impresión de Documentos PDF

Bienvenido a la Aplicación de Impresión de Documentos PDF. Este proyecto permite enviar documentos PDF a impresoras locales a través de una interfaz gráfica y una pequeña API. Los usuarios pueden seleccionar una impresora de una lista y enviar documentos para su impresión de manera sencilla y eficiente.

<p align="center">
  <img src="https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif" alt="Impresión en proceso" width="300" height="200">
</p>

## ✨ Características Principales
- 🎛️ **Interfaz gráfica intuitiva:** Permite seleccionar impresoras disponibles y enviar documentos a imprimir.
- 📜 **Impresión de documentos PDF:** Compatibilidad con archivos PDF sin necesidad de software adicional.
- 🔧 **Soporte para múltiples impresoras:** Obtiene la lista de impresoras disponibles en el sistema.
- 🚀 **API para integración:** Permite a otras aplicaciones enviar documentos a imprimir mediante solicitudes HTTP.

## 🛠️ Stack Tecnológico
- **Python**: Lenguaje principal para la lógica del servidor.
- **Flask**: Framework liviano para la API y la interfaz gráfica.
- **Flask-Cors**: Permite solicitudes desde distintos orígenes.
- **Bootstrap**: Mejora la apariencia de la interfaz.
- **PDFium**: Renderiza documentos PDF.
- **pdftopng**: Convierte PDFs en imágenes para vista previa.
- **Pillow**: Manipulación de imágenes.
- **pywin32**: Interacción con impresoras en Windows.

## 💻 Guía de Instalación
```bash
# 1. Clona el repositorio
git clone https://github.com/DaniAndries/ePrint.git

# 2. Accede al directorio
cd ePrint

# 3. Crea y activa un entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 4. Instala dependencias
pip install -r requirements.txt
```

## 🚀 Instrucciones de Uso
```bash
# Iniciar la aplicación
flask run
```

Luego, accede a `http://127.0.0.1:19191/` en tu navegador para seleccionar una impresora y enviar documentos a imprimir.

## 📡 API Endpoints
- `GET /printers` → Obtiene la lista de impresoras disponibles.
- `POST /printers/{printer_id}` → Envía un documento PDF a la impresora especificada.

## 📜 Licencia
Este proyecto está disponible bajo la licencia MIT.

---

<p align="center">
  🎉 ¡Gracias por usar la Aplicación de Impresión de Documentos PDF! 🎉
</p>

