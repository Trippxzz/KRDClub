/* ==============================================
   KRD Club - Filtro de Vehículos
   ============================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const filtroMarca = document.getElementById('filtro-marca');
    const filtroModelo = document.getElementById('filtro-modelo');
    const filtroCilindrada = document.getElementById('filtro-cilindrada');
    const filtroAnio = document.getElementById('filtro-anio');
    const btnBuscar = document.getElementById('btn-buscar-vehiculo');
    const filtroMensaje = document.getElementById('filtro-mensaje');

    // Verificar si los elementos existen
    if (!filtroMarca) return;

    // ============ CUANDO CAMBIA LA MARCA ============
    filtroMarca.addEventListener('change', async function() {
        const marca = this.value;
        
        // Resetear selects dependientes
        filtroModelo.innerHTML = '<option value="">Cargando...</option>';
        filtroModelo.disabled = true;
        filtroCilindrada.innerHTML = '<option value="">Selecciona modelo</option>';
        filtroCilindrada.disabled = true;
        filtroAnio.innerHTML = '<option value="">Selecciona cilindrada</option>';
        filtroAnio.disabled = true;
        btnBuscar.disabled = true;
        
        if (marca) {
            try {
                const response = await fetch(`/api/modelos/?marca=${encodeURIComponent(marca)}`);
                const data = await response.json();
                
                filtroModelo.innerHTML = '<option value="">Seleccionar modelo</option>';
                data.modelos.forEach(modelo => {
                    filtroModelo.innerHTML += `<option value="${modelo}">${modelo}</option>`;
                });
                filtroModelo.disabled = false;
            } catch (error) {
                console.error('Error al cargar modelos:', error);
                filtroModelo.innerHTML = '<option value="">Error al cargar</option>';
            }
        } else {
            filtroModelo.innerHTML = '<option value="">Primero selecciona marca</option>';
        }
    });

    // ============ CUANDO CAMBIA EL MODELO ============
    filtroModelo.addEventListener('change', async function() {
        const marca = filtroMarca.value;
        const modelo = this.value;
        
        // Resetear selects dependientes
        filtroCilindrada.innerHTML = '<option value="">Cargando...</option>';
        filtroCilindrada.disabled = true;
        filtroAnio.innerHTML = '<option value="">Selecciona cilindrada</option>';
        filtroAnio.disabled = true;
        btnBuscar.disabled = true;
        
        if (modelo) {
            try {
                const response = await fetch(`/api/cilindradas/?marca=${encodeURIComponent(marca)}&modelo=${encodeURIComponent(modelo)}`);
                const data = await response.json();
                
                filtroCilindrada.innerHTML = '<option value="">Seleccionar cilindrada</option>';
                data.cilindradas.forEach(cil => {
                    filtroCilindrada.innerHTML += `<option value="${cil}">${cil}L</option>`;
                });
                filtroCilindrada.disabled = false;
            } catch (error) {
                console.error('Error al cargar cilindradas:', error);
                filtroCilindrada.innerHTML = '<option value="">Error al cargar</option>';
            }
        } else {
            filtroCilindrada.innerHTML = '<option value="">Selecciona modelo</option>';
        }
    });

    // ============ CUANDO CAMBIA LA CILINDRADA ============
    filtroCilindrada.addEventListener('change', async function() {
        const marca = filtroMarca.value;
        const modelo = filtroModelo.value;
        const cilindrada = this.value;
        
        // Resetear año
        filtroAnio.innerHTML = '<option value="">Cargando...</option>';
        filtroAnio.disabled = true;
        btnBuscar.disabled = true;
        
        if (cilindrada) {
            try {
                const response = await fetch(`/api/anios/?marca=${encodeURIComponent(marca)}&modelo=${encodeURIComponent(modelo)}&cilindrada=${encodeURIComponent(cilindrada)}`);
                const data = await response.json();
                
                filtroAnio.innerHTML = '<option value="">Seleccionar año</option>';
                data.anios.forEach(anio => {
                    filtroAnio.innerHTML += `<option value="${anio}">${anio}</option>`;
                });
                filtroAnio.disabled = false;
            } catch (error) {
                console.error('Error al cargar años:', error);
                filtroAnio.innerHTML = '<option value="">Error al cargar</option>';
            }
        } else {
            filtroAnio.innerHTML = '<option value="">Selecciona cilindrada</option>';
        }
    });

    // ============ CUANDO CAMBIA EL AÑO ============
    filtroAnio.addEventListener('change', function() {
        btnBuscar.disabled = !this.value;
    });

    // ============ BOTÓN BUSCAR ============
    btnBuscar.addEventListener('click', async function() {
        const marca = filtroMarca.value;
        const modelo = filtroModelo.value;
        const cilindrada = filtroCilindrada.value;
        const anio = filtroAnio.value;
        
        if (!marca || !modelo || !cilindrada || !anio) {
            mostrarMensaje('Por favor completa todos los campos', 'error');
            return;
        }
        
        btnBuscar.disabled = true;
        btnBuscar.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Buscando...';
        
        try {
            const response = await fetch(`/api/buscar-vehiculo/?marca=${encodeURIComponent(marca)}&modelo=${encodeURIComponent(modelo)}&cilindrada=${encodeURIComponent(cilindrada)}&anio=${encodeURIComponent(anio)}`);
            const data = await response.json();
            
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                mostrarMensaje(data.message, 'error');
                btnBuscar.disabled = false;
                btnBuscar.innerHTML = '<i class="fas fa-search mr-2"></i>Buscar';
            }
        } catch (error) {
            console.error('Error en la búsqueda:', error);
            mostrarMensaje('Error al realizar la búsqueda', 'error');
            btnBuscar.disabled = false;
            btnBuscar.innerHTML = '<i class="fas fa-search mr-2"></i>Buscar';
        }
    });

    // ============ FUNCIÓN MOSTRAR MENSAJE ============
    function mostrarMensaje(texto, tipo) {
        if (!filtroMensaje) return;
        
        filtroMensaje.classList.remove('hidden');
        const p = filtroMensaje.querySelector('p');
        p.textContent = texto;
        p.className = tipo === 'error' ? 'text-red-500' : 'text-green-500';
        
        setTimeout(() => {
            filtroMensaje.classList.add('hidden');
        }, 4000);
    }
});
