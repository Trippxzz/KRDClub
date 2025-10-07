document.addEventListener("DOMContentLoaded", function () {
  const formsetContainer = document.getElementById("productos-formset");
  const addFormBtn = document.getElementById("add-form");
  const totalForms = document.querySelector("#id_productocompra_set-TOTAL_FORMS");

  function bindRowCalculations(row) {
    const inputs = row.querySelectorAll("input, select");
    inputs.forEach((inp) => inp.addEventListener("input", calcularTotales));
  }

  function calcularTotales() {
    const rows = formsetContainer.querySelectorAll(".producto-row");
    let totalNeto = 0;
    rows.forEach((row) => {
      let unidades = parseFloat(row.querySelector("input[name$='cantidad_compra']").value) || 0;
      let precioCompra = parseFloat(row.querySelector("input[name$='precio_und']").value) || 0;
      const subtotal = unidades * precioCompra;
      row.querySelector(".subtotal").innerText = subtotal;
      totalNeto += subtotal;
    });
    const iva = totalNeto * 0.19;
    const totalCompra = totalNeto + iva;
    document.getElementById("total-neto").innerText = totalNeto;
    document.getElementById("iva").innerText = iva;
    document.getElementById("total-compra").innerText = totalCompra;
  }

  function addNewForm() {
    const tmpl = document.getElementById("empty-form-template");
    const clone = tmpl.content.cloneNode(true);
    const index = parseInt(totalForms.value, 10);
    // Reemplazar __prefix__ en name, id y for
    clone.querySelectorAll("input, select, label").forEach((el) => {
      if (el.name) el.name = el.name.replace(/__prefix__/, index);
      if (el.id) el.id = el.id.replace(/__prefix__/, index);
      if (el.getAttribute && el.getAttribute("for")) {
        el.setAttribute("for", el.getAttribute("for").replace(/__prefix__/, index));
      }
      if (el.tagName === "INPUT") {
        if (el.type === "checkbox" || el.type === "radio") {
          el.checked = false;
        } else {
          el.value = "";
        }
      }
    });
    const row = clone.querySelector(".producto-row");
    formsetContainer.appendChild(clone);
    totalForms.value = index + 1;
    bindRowCalculations(formsetContainer.lastElementChild);
    calcularTotales();
  }

  // Inicializar filas existentes
  formsetContainer.querySelectorAll(".producto-row").forEach(bindRowCalculations);
  calcularTotales();

  addFormBtn.addEventListener("click", addNewForm);
});
