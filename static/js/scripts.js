function post_file(event) {
  event.preventDefault();

  const submitButton = document.querySelector('button[type="submit"]');
  const originalText = submitButton.textContent;
  submitButton.textContent = "Enviando...";
  submitButton.disabled = true;

  let formData = new FormData();
  formData.append("copies", document.getElementById("copiesNumber").value);

  let fileInput = document.getElementById("formatField").files[0];
  if (!fileInput) {
    alert("Por favor, selecciona un archivo.");
    resetSubmitButton();
    return;
  }
  formData.append("format", fileInput);

  const driverInput = document.querySelector('input[name="driver"]:checked');
  if (driverInput) {
    formData.append("driver", driverInput.value);
  } else {
    alert("Por favor, selecciona un modo de impresión.");
    resetSubmitButton();
    return;
  }

  let printerSelect = document.getElementById("printerSelect");
  let printerId = printerSelect.value;
  if (!printerId || printerSelect.options.length === 0) {
    alert("Por favor, selecciona una impresora válida.");
    resetSubmitButton();
    return;
  }

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
      document.getElementById("form-1").reset();
      loadPrinters();
    })
    .catch((error) => {
      console.error("Error:", error);
      alert(`Error: ${error.message || "Problema al enviar el documento a imprimir"}`);
    })
    .finally(resetSubmitButton);
}

function resetSubmitButton() {
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.textContent = "Enviar";
  submitButton.disabled = false;
}

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
      printerSelect.innerHTML = "";

      if (!Array.isArray(printers) || printers.length === 0) {
        printerSelect.innerHTML = '<option value="">No se encontraron impresoras</option>';
        return;
      }

      printers.forEach((printer) => {
        const option = document.createElement("option");
        option.value = printer.name;
        option.textContent = printer.name;
        option.setAttribute("data-duplex", printer.duplex.toString());
        printerSelect.appendChild(option);
      });

      printerSelect.dispatchEvent(new Event("change"));
    })
    .catch((error) => {
      console.error("Error al cargar impresoras:", error);
      printerSelect.innerHTML = '<option value="">Error al cargar impresoras</option>';
    });
}

document.addEventListener("DOMContentLoaded", function () {
  loadPrinters();

  document.getElementById("printerSelect").addEventListener("change", function () {
    if (this.selectedIndex < 0) return;

    let selectedOption = this.options[this.selectedIndex];
    let duplex = selectedOption.getAttribute("data-duplex") === "true";
    let radioDobleCara = document.getElementById("r2");

    radioDobleCara.disabled = !duplex;
    if (!duplex) {
      document.getElementById("r1").checked = true;
    }
  });

  document.getElementById("form-1").addEventListener("submit", post_file);
});
