# 🖨️ Aplicación de Impresión de Documentos PDF

Esta aplicación proporciona una interfaz gráfica y una API para seleccionar una impresora y enviar documentos PDF a imprimir de manera sencilla.

## ✨ Características Principales
- 🌐 **Interfaz web intuitiva** para la selección de impresoras y envío de documentos.
- 📄 **Soporte para archivos PDF** con conversión de imagen previa a la impresión.
- 🔄 **Gestor de trabajos de impresión** con información detallada de impresoras disponibles.
- 🔒 **Compatibilidad con Windows** mediante el uso de `pywin32` para la gestión de impresoras.

## 🛠️ Tecnologías Utilizadas
- **Bootstrap**: Interfaz web responsiva.
- **Flask & Flask-Cors**: Backend y API REST.
- **PDFium & pdftopng**: Conversión de documentos PDF.
- **Pillow**: Manipulación de imágenes.
- **pywin32**: Manejo de impresoras en Windows.

## 📌 Endpoints de la API

### General
#### `GET /`
Devuelve la página de inicio de la aplicación.

### Administración
#### `GET /management/about`
Obtiene información del sistema.

#### `GET /management/print`
Lista las impresoras disponibles.

#### `GET /management/versions`
Obtiene las versiones de la aplicación.

#### `GET /management/docs`
Obtiene información de la API.

### Impresoras
#### `GET /printers`
Obtiene la lista de impresoras disponibles en el equipo.

#### `POST /printers/{printer_id}`
Envía un documento a la impresora especificada.

### Configuración

#### GET /management/settings
Obtiene los ajustes de la impresora

#### POST /management/settings
Guarda los ajustes de la impresora

### Licencias

#### GET /management/licenses
Obtiene información sobre licencias

## 🚀 Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/tuusuario/tu-repositorio.git

# 2. Navegar al directorio del proyecto
cd tu-repositorio

# 3. Crear un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
flask run
```

## 🎯 Uso

1. Iniciar la aplicación.
2. Acceder a la interfaz web.
3. Seleccionar una impresora disponible.
4. Subir un documento PDF y enviarlo a imprimir.

## 🤝 Colaboradores
Este proyecto ha sido desarrollado en colaboración con:

- [JoseAngelHub](https://github.com/JoseAngelHub)
- [DaniAndries](https://github.com/DaniAndries)

## 📄 Licencia
Este proyecto se distribuye bajo la licencia MIT.

