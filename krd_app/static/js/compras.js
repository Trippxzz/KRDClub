document.addEventListener("DOMContentLoaded", function() {
    const rows = document.querySelectorAll(".producto-row");

    function calcularTotales() {
        let totalNeto = 0;

        rows.forEach(row => {
            let unidades = row.querySelector("input[name$='cantidad_compra']").value || 0;
            let precioCompra = row.querySelector("input[name$='precio_und']").value || 0;

            unidades = parseFloat(unidades) || 0;
            precioCompra = parseFloat(precioCompra) || 0;

            let subtotal = unidades * precioCompra;
            row.querySelector(".subtotal").innerText = subtotal.toFixed(2);

            totalNeto += subtotal;
        });

        // Calcular IVA (19%)
        let iva = totalNeto * 0.19;
        let totalCompra = totalNeto + iva;

        // Mostrar en la vista
        document.getElementById("total-neto").innerText = totalNeto.toFixed(2);
        document.getElementById("iva").innerText = iva.toFixed(2);
        document.getElementById("total-compra").innerText = totalCompra.toFixed(2);
    }

    // Ejecutar al cargar
    calcularTotales();

    // Ejecutar cada vez que se cambien valores
    rows.forEach(row => {
        row.querySelectorAll("input").forEach(input => {
            input.addEventListener("input", calcularTotales);
        });
    });
});

