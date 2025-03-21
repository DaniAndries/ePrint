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
  formData.append("file", fileInput);

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

function saveSettings(event) {
  event.preventDefault();

  const printer = document.getElementById("printerSelect").value;
  const copies = document.getElementById("copiesNumber").value;
  const sides = document.querySelector('input[name="sides"]:checked')?.value;
  const dpi = document.getElementById("dpi").value;

  if (!printer || !copies || !sides || !dpi) {
    alert("Por favor, complete todos los campos.");
    return;
  }

  fetch("/management/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ printer, copies, sides, dpi }),
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
    })
    .catch((error) => {
      console.error("Error al guardar configuración:", error);
      alert("Error al guardar configuración.");
    });
}

// Funcion que restaura el texto y habilita el boton de envio
function resetSubmitButton() {
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.textContent = "Enviar";
  submitButton.disabled = false;
}

// Funcion para cargar la lista de impresoras disponibles
let printersData = {}; // Objeto global para almacenar los datos de las impresoras

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
      printerSelect.innerHTML = ""; // Limpia opciones previas
      printersData = {}; // Reinicia el objeto global

      if (!Array.isArray(printers) || printers.length === 0) {
        printerSelect.innerHTML =
          '<option value="">No se encontraron impresoras</option>';
        return;
      }

      printers.forEach((printer) => {
        // Almacena la configuracion en el objeto global
        printersData[printer.name] = printer;

        // Agrega la impresora al select
        const option = document.createElement("option");
        option.value = printer.name;
        option.textContent = printer.name;
        option.setAttribute("data-duplex", printer.duplex.toString());
        printerSelect.appendChild(option);
      });

      // Dispara un evento para actualizar la seleccion con la primera impresora disponible
      printerSelect.dispatchEvent(new Event("change"));
    })
    .catch((error) => {
      console.error("Error al cargar impresoras:", error);
      printerSelect.innerHTML =
        '<option value="">Error al cargar impresoras</option>';
    });
}

// Funcion para actualizar los campos del formulario segun la impresora seleccionada
function updateFormFields() {
  const printerSelect = document.getElementById("printerSelect");
  const selectedPrinter = printerSelect.value;
  if (!selectedPrinter || !printersData[selectedPrinter]) return;

  const printerConfig = printersData[selectedPrinter];
  if (window.location.pathname.includes("settings")) {
    document.getElementById("600").disabled = false;
    document.getElementById("300").disabled = false;
    if (printerConfig.max_dpi < 600)
      document.getElementById("600").disabled = true;
    if (printerConfig.max_dpi < 300)
      document.getElementById("300").disabled = true;
  }
  document.getElementById("copiesNumber").value = printerConfig.copies || 1;
  document.getElementById("dpi").value = printerConfig.dpi || 203;
  // Habilita/deshabilita impresion a doble cara
  let radioDobleCara = document.getElementById("r2");
  radioDobleCara.disabled = !printerConfig.duplex;
  if (!printerConfig.duplex) {
    document.getElementById("r1").checked = true; // Forzar una cara si no hay duplex
  } else {
    radioDobleCara.checked = printerConfig.sides === 2;
  }
  if (window.location.pathname.includes("settings")) {
    let radioFormatoZPL = document.getElementById("r4");
    if (radioFormatoZPL.checked) {
      document.getElementById("r2").disabled = true;
    }
  }
}

if (window.location.pathname.includes("settings")) {
  const pdf = document.getElementById("r3");
  const zpl = document.getElementById("r4");

  pdf.addEventListener("click", function () {
    if (pdf.checked) {
      document.getElementById("dpi").disabled = true;
      document.getElementById("r1").disabled = false;
      document.getElementById("r2").disabled = false;
      const printerSelect = document.getElementById("printerSelect");
      const selectedPrinter = printerSelect.value;
      const printerConfig = printersData[selectedPrinter];
      let radioDobleCara = document.getElementById("r2");
      radioDobleCara.disabled = !printerConfig.duplex;
      if (!printerConfig.duplex) {
        document.getElementById("r1").checked = true; // Forzar una cara si no hay duplex
      } else {
        radioDobleCara.checked = printerConfig.sides === 2;
      }
    }
  });
  zpl.addEventListener("click", function () {
    document.getElementById("dpi").disabled = false;
    document.getElementById("r1").disabled = true;
    document.getElementById("r2").disabled = true;
  });
}
// Evento que se dispara cuando la pagina se ha cargado completamente
document.addEventListener("DOMContentLoaded", function () {
  loadPrinters();
  updateFormFields();
  if (window.location.pathname.includes("settings")) {
    const form = document.getElementById("printerSettingsForm");
    if (form) {
      form.addEventListener("submit", saveSettings);
    } else {
      console.error("No se encontró el formulario printerSettingsForm");
    }
  }

  if (window.location.pathname.includes("management/print")) {
    const form = document.getElementById("form-1");
    if (form) {
      form.addEventListener("submit", post_file);
    } else {
      console.error("No se encontró el formulario form-1");
    }
  }

  // Verifica que el selector de impresoras exista antes de asignarle un evento
  const printerSelect = document.getElementById("printerSelect");
  if (printerSelect) {
    printerSelect.addEventListener("change", updateFormFields);
  } else {
    console.error("No se encontró el selector de impresoras");
  }
});
