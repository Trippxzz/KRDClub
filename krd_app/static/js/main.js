/* ==============================================
   KRD Club - JavaScript Principal
   ============================================== */

// ============ NAVBAR MOBILE ============
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });

        // Cerrar menú al hacer clic en un enlace
        const menuLinks = mobileMenu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
            });
        });
    }
});

// ============ CONTADOR CARRITO ============
function actualizarContadorCarrito() {
    const contadorElement = document.getElementById('carrito-contador');
    if (!contadorElement) return;
    
    fetch('/contador_carrito/')
        .then(response => response.json())
        .then(data => {
            contadorElement.textContent = data.total_items || 0;
        })
        .catch(error => {
            console.error('Error al actualizar contador:', error);
            contadorElement.textContent = '0';
        });
}

// Actualizar contador al cargar la página
document.addEventListener('DOMContentLoaded', actualizarContadorCarrito);

// ============ UTILIDADES ============
function formatPrice(price) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        minimumFractionDigits: 0
    }).format(price);
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} animate-fadeIn`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-4 font-bold">&times;</button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ============ SCROLL SUAVE ============
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
