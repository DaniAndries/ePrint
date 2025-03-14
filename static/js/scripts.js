// Funcion que maneja el envio del archivo al servidor
function post_file(event) {
  event.preventDefault(); // Prevenir el comportamiento por defecto del formulario

  const submitButton = document.querySelector('button[type="submit"]');
  const originalText = submitButton.textContent;
  submitButton.textContent = "Enviando..."; // Cambia el texto del boton a "Enviando..."
  submitButton.disabled = true; // Desactiva el boton para evitar envios multiples

  let formData = new FormData();
  // Agrega el numero de copias al formulario
  formData.append("copies", document.getElementById("copiesNumber").value);

  let fileInput = document.getElementById("formatField").files[0];
  if (!fileInput) {
    alert("Por favor, selecciona un archivo.");
    resetSubmitButton(); // Restaura el boton si no hay archivo
    return;
  }
  formData.append("format", fileInput);

  const driverInput = document.querySelector('input[name="driver"]:checked');
  if (driverInput) {
    formData.append("driver", driverInput.value); // Agrega el modo de impresion seleccionado
  } else {
    alert("Por favor, selecciona un modo de impresión.");
    resetSubmitButton(); // Restaura el boton si no se selecciona un modo
    return;
  }

  let printerSelect = document.getElementById("printerSelect");
  let printerId = printerSelect.value;
  if (!printerId || printerSelect.options.length === 0) {
    alert("Por favor, selecciona una impresora válida.");
    resetSubmitButton(); // Restaura el boton si no se selecciona impresora
    return;
  }

  // Realiza la peticion POST para enviar el archivo a la impresora
  fetch(`/printers/${encodeURIComponent(printerId)}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      return response.text().then((text) => {
        if (!response.ok) {
          try {
            const data = JSON.parse(text);
            throw new Error(
              data.error || `Error en el servidor (${response.status})`
            );
          } catch {
            throw new Error(`Error desconocido: ${text}`);
          }
        }
        return JSON.parse(text);
      });
    })
    .then((data) => {
      alert(data.message || "Documento enviado correctamente");
      document.getElementById("form-1").reset(); // Resetea el formulario despues de enviar
      loadPrinters(); // Recarga la lista de impresoras
    })
    .catch((error) => {
      console.error("Error:", error);
      alert(
        `Error: ${
          error.message || "Problema al enviar el documento a imprimir"
        }`
      );
    })
    .finally(resetSubmitButton); // Restaura el boton al final
}

// Funcion que restaura el texto y habilita el boton de envio
function resetSubmitButton() {
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.textContent = "Enviar";
  submitButton.disabled = false;
}

// Funcion para cargar la lista de impresoras disponibles
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
      printerSelect.innerHTML = ""; // Limpia las opciones previas

      if (!Array.isArray(printers) || printers.length === 0) {
        printerSelect.innerHTML =
          '<option value="">No se encontraron impresoras</option>';
        return;
      }

      // Agrega las impresoras encontradas como opciones al select
      printers.forEach((printer) => {
        const option = document.createElement("option");
        option.value = printer.name;
        option.textContent = printer.name;
        option.setAttribute("data-duplex", printer.duplex.toString());
        printerSelect.appendChild(option);
      });

      // Dispara un evento para actualizar la seleccion
      printerSelect.dispatchEvent(new Event("change"));
    })
    .catch((error) => {
      console.error("Error al cargar impresoras:", error);
      printerSelect.innerHTML =
        '<option value="">Error al cargar impresoras</option>';
    });
}

// Evento que se dispara cuando la pagina se ha cargado completamente
document.addEventListener("DOMContentLoaded", function () {
  loadPrinters(); // Carga las impresoras disponibles al iniciar

  // Maneja el cambio de seleccion de la impresora
  document
    .getElementById("printerSelect")
    .addEventListener("change", function () {
      if (this.selectedIndex < 0) return;

      let selectedOption = this.options[this.selectedIndex];
      let duplex = selectedOption.getAttribute("data-duplex") === "true";
      let radioDobleCara = document.getElementById("r2");

      radioDobleCara.disabled = !duplex; // Deshabilita la opcion de doble cara si la impresora no lo soporta
      if (!duplex) {
        document.getElementById("r1").checked = true; // Selecciona el modo de una sola cara si no se soporta duplex
      }
    });

  // Asocia la funcion de envio al formulario
  document.getElementById("form-1").addEventListener("submit", post_file);
});
