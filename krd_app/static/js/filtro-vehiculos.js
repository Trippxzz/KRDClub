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

    // ============ MAPEO DE MARCAS A IDs DE FONDO ============
    const marcaBackgrounds = {
        'bmw': 'vehicle-bg-bmw',
        'mercedes': 'vehicle-bg-mercedes',
        'mercedes-benz': 'vehicle-bg-mercedes',
        'mercedes benz': 'vehicle-bg-mercedes',
        'audi': 'vehicle-bg-audi',
        'porsche': 'vehicle-bg-porsche',
        'ferrari': 'vehicle-bg-ferrari',
        'lamborghini': 'vehicle-bg-lamborghini',
        'maserati': 'vehicle-bg-maserati',
        'lexus': 'vehicle-bg-lexus',
        'jaguar': 'vehicle-bg-jaguar',
        'bentley': 'vehicle-bg-bentley',
        'rolls-royce': 'vehicle-bg-rollsroyce',
        'rolls royce': 'vehicle-bg-rollsroyce',
        'land rover': 'vehicle-bg-landrover',
        'land-rover': 'vehicle-bg-landrover',
        'range rover': 'vehicle-bg-landrover'
    };

    // ============ FUNCIÓN CAMBIAR FONDO ============
    function cambiarFondo(marca) {
        // Obtener todas las imágenes de fondo
        const allBgs = document.querySelectorAll('.vehicle-bg-image');
        const defaultBg = document.getElementById('vehicle-bg-default');
        
        if (!allBgs.length) return;
        
        // Normalizar la marca a minúsculas
        const marcaNormalizada = marca ? marca.toLowerCase().trim() : '';
        
        // Buscar el fondo correspondiente
        let targetBgId = marcaBackgrounds[marcaNormalizada];
        let targetBg = targetBgId ? document.getElementById(targetBgId) : null;
        
        // Si no hay fondo específico, usar el default
        if (!targetBg) {
            targetBg = defaultBg;
        }
        
        // Remover clase active de todos
        allBgs.forEach(bg => bg.classList.remove('active'));
        
        // Agregar clase active al fondo objetivo
        if (targetBg) {
            targetBg.classList.add('active');
        }
    }

    // ============ CUANDO CAMBIA LA MARCA ============
    filtroMarca.addEventListener('change', async function() {
        const marca = this.value;
        
        // Cambiar el fondo según la marca
        cambiarFondo(marca);
        
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
            // Volver al fondo por defecto
            cambiarFondo('');
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
                btnBuscar.innerHTML = '<i class="fas fa-search"></i><span>BUSCAR</span>';
            }
        } catch (error) {
            console.error('Error en la búsqueda:', error);
            mostrarMensaje('Error al realizar la búsqueda', 'error');
            btnBuscar.disabled = false;
            btnBuscar.innerHTML = '<i class="fas fa-search"></i><span>BUSCAR</span>';
        }
    });

    // ============ FUNCIÓN MOSTRAR MENSAJE ============
    function mostrarMensaje(texto, tipo) {
        if (!filtroMensaje) return;
        
        filtroMensaje.classList.remove('hidden');
        const p = filtroMensaje.querySelector('p');
        p.textContent = texto;
        p.className = tipo === 'error' 
            ? 'text-red-400 bg-red-500/20 rounded-lg py-3 px-6 inline-block' 
            : 'text-green-400 bg-green-500/20 rounded-lg py-3 px-6 inline-block';
        
        setTimeout(() => {
            filtroMensaje.classList.add('hidden');
        }, 4000);
    }
});
