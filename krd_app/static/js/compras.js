
// --- Lógica de compras (solo si existen los elementos de compras) ---
document.addEventListener('DOMContentLoaded', function() {
  const addBtn = document.getElementById("add-product");
  const tbody = document.getElementById("productos-body");
  const templateEl = document.getElementById("producto-row-template");
  const totalNetoEl = document.getElementById("total-neto");
  const ivaEl = document.getElementById("iva");
  const totalCompraEl = document.getElementById("total-compra");
  const productosDataInput = document.getElementById("productos_data");

  if (addBtn && tbody && templateEl && totalNetoEl && ivaEl && totalCompraEl && productosDataInput) {
    const template = templateEl.content;
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
  }

  // --- Lógica de imágenes (siempre que exista el input de imágenes) ---
  const input = document.getElementById('id_imagenes');
  if (input) {
    input.addEventListener('change', mostrarPreviewYRadios);
  }
});

function mostrarPreviewYRadios() {
    const input = document.getElementById('id_imagenes');
    const preview = document.getElementById('preview_imagenes');
    preview.innerHTML = '';
    const files = input.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();
        const div = document.createElement('div');
        div.style.display = 'inline-block';
        div.style.margin = '10px';
        // Radio para marcar principal. Por defecto, la primera está seleccionada
        div.innerHTML = `<input type='radio' name='principal_radio' value='${i}' ${i===0?'checked':''} onchange='document.getElementById("principal_idx").value=${i}'> Principal<br>`;
        reader.onload = function(e) {
            div.innerHTML += `<img src='${e.target.result}' style='max-width:100px;max-height:100px;display:block;'>`;
        };
        reader.readAsDataURL(file);
        preview.appendChild(div);
    }
    // Si el usuario cambia el radio, actualiza el input hidden
    document.querySelectorAll("input[name='principal_radio']").forEach(radio => {
        radio.addEventListener('change', function() {
            document.getElementById('principal_idx').value = this.value;
        });
    });
}