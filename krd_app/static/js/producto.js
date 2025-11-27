/**
 * Producto Detalle - JavaScript específico
 * Funciones para cantidad y carrito
 */

// Variables globales (serán inicializadas desde el template)
let maxStock = 1;

/**
 * Inicializa el módulo con el stock del producto
 */
function initProducto(stock) {
    maxStock = stock;
    setupEventListeners();
}

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    const form = document.getElementById('form-agregar-carrito');
    if (form) {
        form.addEventListener('submit', handleAgregarCarrito);
    }
}

/**
 * Decrementa la cantidad del producto
 */
function decrementarCantidad() {
    const input = document.getElementById('cantidad');
    if (input) {
        const currentValue = parseInt(input.value) || 1;
        input.value = Math.max(1, currentValue - 1);
    }
}

/**
 * Incrementa la cantidad del producto
 */
function incrementarCantidad() {
    const input = document.getElementById('cantidad');
    if (input) {
        const currentValue = parseInt(input.value) || 1;
        input.value = Math.min(maxStock, currentValue + 1);
    }
}

/**
 * Maneja el envío del formulario de agregar al carrito
 */
function handleAgregarCarrito(e) {
    e.preventDefault();
    const form = e.target;
    const cantidad = form.cantidad ? form.cantidad.value : 1;
    const url = form.action + '?cantidad=' + encodeURIComponent(cantidad);
    
    fetch(url, { 
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        // Mostrar notificación
        mostrarNotificacion();
        
        // Actualizar contador del carrito si existe la función global
        if (typeof window.actualizarContadorCarrito === 'function') {
            window.actualizarContadorCarrito();
        }
    })
    .catch(err => {
        console.error('Error al agregar al carrito:', err);
        // En caso de error, redirigir normalmente
        window.location.href = url;
    });
}

/**
 * Muestra la notificación de producto agregado
 */
function mostrarNotificacion() {
    const notif = document.getElementById('notificacion-carrito');
    if (notif) {
        notif.classList.add('show');
        notif.style.display = 'flex';
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notif.classList.remove('show');
            notif.style.display = 'none';
        }, 3000);
    }
}

/**
 * Cambia la imagen principal al hacer clic en un thumbnail
 */
function cambiarImagenPrincipal(url) {
    const imgPrincipal = document.getElementById('imagen-principal');
    if (imgPrincipal) {
        imgPrincipal.src = url;
        
        // Actualizar estado activo de thumbnails
        document.querySelectorAll('.producto-thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
            if (thumb.dataset.url === url) {
                thumb.classList.add('active');
            }
        });
    }
}

// Exponer funciones globalmente para uso en onclick
window.decrementarCantidad = decrementarCantidad;
window.incrementarCantidad = incrementarCantidad;
window.cambiarImagenPrincipal = cambiarImagenPrincipal;
window.initProducto = initProducto;
