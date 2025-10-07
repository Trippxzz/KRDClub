const addBtn = document.getElementById("add-product");
const tbody = document.getElementById("productos-body");
const template = document.getElementById("producto-row-template").content;
const totalNetoEl = document.getElementById("total-neto");
const ivaEl = document.getElementById("iva");
const totalCompraEl = document.getElementById("total-compra");
const productosDataInput = document.getElementById("productos_data");

function calcularTotales() {
  let total = 0;
  tbody.querySelectorAll("tr").forEach(row => {
    const cant = parseFloat(row.querySelector(".cantidad-input").value) || 0;
    const precio = parseFloat(row.querySelector(".precio-input").value) || 0;
    const subtotal = cant * precio;
    row.querySelector(".subtotal").innerText = subtotal.toFixed(2);
    total += subtotal;
  });
  totalNetoEl.innerText = total.toFixed(2);
  const iva = total * 0.19;
  ivaEl.innerText = iva.toFixed(2);
  totalCompraEl.innerText = (total + iva).toFixed(2);
}

function agregarProducto() {
  const clone = document.importNode(template, true);
  const row = clone.querySelector("tr");

  row.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("input", calcularTotales);
  });

  row.querySelector(".btn-eliminar").addEventListener("click", () => {
    row.remove();
    calcularTotales();
  });

  tbody.appendChild(row);
  calcularTotales();
}

addBtn.addEventListener("click", agregarProducto);

document.querySelector("form").addEventListener("submit", (e) => {
  const productos = [];
  tbody.querySelectorAll("tr").forEach(row => {
    productos.push({
      producto: row.querySelector(".producto-select").value,
      cantidad: row.querySelector(".cantidad-input").value,
      precio: row.querySelector(".precio-input").value
    });
  });
  productosDataInput.value = JSON.stringify(productos);
});