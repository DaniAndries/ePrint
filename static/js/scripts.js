// Función que maneja el envío del archivo al servidor
function post_file(event) {
  event.preventDefault(); // Prevenir el comportamiento por defecto del formulario

  const submitButton = document.querySelector('button[type="submit"]');
  const originalText = submitButton.textContent;
  submitButton.textContent = "Enviando..."; // Cambia el texto del botón a "Enviando..."
  submitButton.disabled = true; // Desactiva el botón para evitar envíos múltiples

  let formData = new FormData();
  // Agrega el número de copias al formulario
  formData.append("copies", document.getElementById("copiesNumber").value);

  let fileInput = document.getElementById("formatField").files[0];
  if (!fileInput) {
    alert("Por favor, selecciona un archivo.");
    resetSubmitButton(); // Restaura el botón si no hay archivo
    return;
  }
  formData.append("file", fileInput);

  const driverInput = document.querySelector('input[name="driver"]:checked');
  if (driverInput) {
    formData.append("driver", driverInput.value); // Agrega el modo de impresión seleccionado
  } else {
    alert("Por favor, selecciona un modo de impresión.");
    resetSubmitButton(); // Restaura el botón si no se selecciona un modo
    return;
  }

  let printerSelect = document.getElementById("printerSelect");
  let printerId = printerSelect.value;
  if (!printerId || printerSelect.options.length === 0) {
    alert("Por favor, selecciona una impresora válida.");
    resetSubmitButton(); // Restaura el botón si no se selecciona impresora
    return;
  }

  // Realiza la petición POST para enviar el archivo a la impresora
  fetch(`/printers/${encodeURIComponent(printerId)}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      return response.text().then((text) => {
        if (!response.ok) {
          try {
            const data = JSON.parse(text);
            throw new Error(data.error || `Error en el servidor (${response.status})`);
          } catch {
            throw new Error(`Error desconocido: ${text}`);
          }
        }
        return JSON.parse(text);
      });
    })
    .then((data) => {
      alert(data.message || "Documento enviado correctamente");
      document.getElementById("form-1").reset(); // Resetea el formulario después de enviar
      loadPrinters(); // Recarga la lista de impresoras
    })
    .catch((error) => {
      console.error("Error:", error);
      alert(`Error: ${error.message || "Problema al enviar el documento a imprimir"}`);
    })
    .finally(resetSubmitButton); // Restaura el botón al final
}

// Función que restaura el texto y habilita el botón de envío
function resetSubmitButton() {
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.textContent = "Enviar";
  submitButton.disabled = false;
}

// Función para cargar la lista de impresoras disponibles
let printersData = {}; // Objeto global para almacenar los datos de las impresoras

// Función para cargar la lista de impresoras disponibles
function loadPrinters() {
  const printerSelect = document.getElementById("printerSelect");

  fetch("/printers")
    .then((response) => {
      if (!response.ok) {
        throw new Error("No se pudieron cargar las impresoras");
      }
      return response.json();
    })
    .then((printers) => {
      printerSelect.innerHTML = ""; // Limpia opciones previas
      printersData = {}; // Reinicia el objeto global

      if (!Array.isArray(printers) || printers.length === 0) {
        printerSelect.innerHTML = '<option value="">No se encontraron impresoras</option>';
        return;
      }

      printers.forEach((printer) => {
        // Almacena la configuración en el objeto global
        printersData[printer.name] = printer;

        // Agrega la impresora al select
        const option = document.createElement("option");
        option.value = printer.name;
        option.textContent = printer.name;
        option.setAttribute("data-duplex", printer.duplex.toString());
        printerSelect.appendChild(option);
      });

      // Dispara un evento para actualizar la selección con la primera impresora disponible
      printerSelect.dispatchEvent(new Event("change"));
    })
    .catch((error) => {
      console.error("Error al cargar impresoras:", error);
      printerSelect.innerHTML = '<option value="">Error al cargar impresoras</option>';
    });
}

// Función para actualizar los campos del formulario según la impresora seleccionada
function updateFormFields() {
  const printerSelect = document.getElementById("printerSelect");
  const selectedPrinter = printerSelect.value;

  if (!selectedPrinter || !printersData[selectedPrinter]) return;

  const printerConfig = printersData[selectedPrinter];

  document.getElementById("copiesNumber").value = printerConfig.copies || 1;

  // Habilita/deshabilita impresión a doble cara
  let radioDobleCara = document.getElementById("r2");
  radioDobleCara.disabled = !printerConfig.duplex;
  if (!printerConfig.duplex) {
    document.getElementById("r1").checked = true; // Forzar una cara si no hay duplex
  } else {
    radioDobleCara.checked = printerConfig.sides === 2;
  }
}

// Evento que se dispara cuando la página se ha cargado completamente
document.addEventListener("DOMContentLoaded", function () {
  loadPrinters(); // Carga las impresoras disponibles al iniciar

  // Maneja el cambio de selección de la impresora y actualiza los campos del formulario
  document.getElementById("printerSelect").addEventListener("change", updateFormFields);

  // Asocia la función de envío al formulario
  document.getElementById("form-1").addEventListener("submit", post_file);
});
