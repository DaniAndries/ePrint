🖨️ Aplicación de Impresión de Documentos PDF
Esta aplicación proporciona una interfaz gráfica y una API para seleccionar una impresora y enviar documentos PDF a imprimir de manera sencilla.

✨ Características Principales

🌐 Interfaz web intuitiva para la selección de impresoras y envío de documentos.
📄 Soporte para archivos PDF con conversión de imagen previa a la impresión.
🔄 Gestor de trabajos de impresión con información detallada de impresoras disponibles.
🔒 Compatibilidad con Windows mediante el uso de pywin32 para la gestión de impresoras.

🛠️ Tecnologías Utilizadas

Bootstrap: Interfaz web responsiva.
Flask & Flask-Cors: Backend y API REST.
PDFium & pdftopng: Conversión de documentos PDF.
Pillow: Manipulación de imágenes.
pywin32: Manejo de impresoras en Windows.

📌 Endpoints de la API
General
GET /
Devuelve la página de inicio de la aplicación.

Administración
GET /management/about
Obtiene información del sistema.

GET /management/print
Lista las impresoras disponibles.

GET /management/versions
Obtiene las versiones de la aplicación.

GET /management/docs
Obtiene información de la API.

Impresión
GET /printers
Obtiene la lista de impresoras disponibles en el equipo.

POST /printers/{printer_id}
Envía un documento a la impresora especificada.

🚀 Instalación y Ejecución
