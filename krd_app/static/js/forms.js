/**
 * Formularios - JavaScript común
 * Funciones para manejo de formularios, uploads y selecciones
 */

/**
 * Inicializa el contador de archivos y la validación
 */
function initFileUpload(inputId, counterId, options = {}) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    const checkbox360 = options.checkbox360Id ? document.getElementById(options.checkbox360Id) : null;
    const principalSelector = options.principalSelectorId ? document.getElementById(options.principalSelectorId) : null;
    const principalSelect = options.principalSelectId ? document.getElementById(options.principalSelectId) : null;
    
    if (!input || !counter) return;
    
    // Event listener para el checkbox 360
    if (checkbox360 && principalSelector) {
        checkbox360.addEventListener('change', function() {
            principalSelector.style.display = this.checked ? 'none' : 'block';
        });
    }
    
    // Event listener para el input de archivos
    input.addEventListener('change', function() {
        const numFiles = this.files.length;
        counter.textContent = `${numFiles} imagen(es) seleccionada(s)`;
        counter.className = 'file-counter';
        
        // Validación para 360
        if (checkbox360 && checkbox360.checked) {
            if (numFiles < 24) {
                counter.classList.add('warning');
                counter.textContent += ' ⚠️ (Se recomiendan al menos 24 imágenes)';
            } else if (numFiles > 60) {
                counter.classList.add('info');
                counter.textContent += ' (Se optimizarán a 36 imágenes)';
            } else {
                counter.classList.add('success');
            }
        } else {
            counter.classList.add('success');
        }
        
        // Actualizar selector de imagen principal
        if (principalSelect && (!checkbox360 || !checkbox360.checked)) {
            principalSelect.innerHTML = '';
            for (let i = 0; i < numFiles; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = `Imagen ${i + 1}`;
                principalSelect.appendChild(option);
            }
        }
    });
}

/**
 * Inicializa el área de drag & drop
 */
function initDragDrop(areaId, inputId) {
    const area = document.getElementById(areaId);
    const input = document.getElementById(inputId);
    
    if (!area || !input) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, () => area.classList.add('dragover'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
    });
    
    area.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        input.files = files;
        input.dispatchEvent(new Event('change'));
    }, false);
    
    area.addEventListener('click', function() {
        input.click();
    });
}

/**
 * Gestor de selección de vehículos
 */
class VehicleSelector {
    constructor(options) {
        this.selectId = options.selectId;
        this.addBtnId = options.addBtnId;
        this.tableBodyId = options.tableBodyId;
        this.inputId = options.inputId;
        this.initialDataId = options.initialDataId;
        
        this.vehicles = [];
        this.init();
    }
    
    init() {
        this.select = document.getElementById(this.selectId);
        this.addBtn = document.getElementById(this.addBtnId);
        this.tableBody = document.getElementById(this.tableBodyId);
        this.input = document.getElementById(this.inputId);
        
        if (!this.select || !this.addBtn || !this.tableBody || !this.input) {
            console.log('Elementos de vehículos no encontrados');
            return;
        }
        
        // Cargar datos iniciales
        this.loadInitialData();
        
        // Event listeners
        this.addBtn.addEventListener('click', () => this.addVehicle());
    }
    
    loadInitialData() {
        const dataEl = document.getElementById(this.initialDataId);
        if (dataEl) {
            try {
                const initialVehicles = JSON.parse(dataEl.textContent);
                initialVehicles.forEach(v => {
                    this.vehicles.push({ id: v.id, text: v.text });
                });
                this.updateUI();
            } catch (e) {
                console.error('Error al parsear vehículos iniciales:', e);
            }
        }
        
        // Inicializar tabla vacía si no hay datos
        if (this.vehicles.length === 0) {
            this.updateUI();
        }
    }
    
    addVehicle() {
        const selectedOption = this.select.options[this.select.selectedIndex];
        const vehicleId = selectedOption.value;
        const vehicleText = selectedOption.text;
        
        // Verificar si ya está agregado
        if (this.vehicles.find(v => v.id === vehicleId)) {
            alert('Este vehículo ya está agregado');
            return;
        }
        
        this.vehicles.push({ id: vehicleId, text: vehicleText });
        this.updateUI();
    }
    
    removeVehicle(index) {
        this.vehicles.splice(index, 1);
        this.updateUI();
    }
    
    updateUI() {
        // Actualizar tabla
        this.tableBody.innerHTML = '';
        
        if (this.vehicles.length === 0) {
            this.tableBody.innerHTML = '<tr class="empty-row"><td colspan="2">Sin aplicaciones</td></tr>';
        } else {
            this.vehicles.forEach((v, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${v.text}</td>
                    <td>
                        <button type="button" class="btn-danger btn-small" data-index="${index}">
                            <i class="fas fa-times"></i>
                        </button>
                    </td>
                `;
                this.tableBody.appendChild(row);
            });
            
            // Event listeners para botones de eliminar
            this.tableBody.querySelectorAll('[data-index]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const index = parseInt(btn.getAttribute('data-index'));
                    this.removeVehicle(index);
                });
            });
        }
        
        // Actualizar input hidden
        this.input.value = this.vehicles.map(v => v.id).join(',');
    }
}

/**
 * Muestra notificación después de crear/editar
 */
function showFormNotification(type = 'success', message = 'Operación exitosa') {
    const notif = document.querySelector('.form-notification');
    if (notif) {
        notif.className = `form-notification show ${type}`;
        notif.querySelector('span').textContent = message;
        
        setTimeout(() => {
            notif.classList.remove('show');
        }, 3000);
    }
}

/**
 * Inicializa notificación basada en sessionStorage
 */
function initFormNotification(storageKey, notifId) {
    const notif = document.getElementById(notifId);
    if (sessionStorage.getItem(storageKey) && notif) {
        notif.style.display = 'flex';
        notif.classList.add('show');
        
        setTimeout(() => {
            sessionStorage.removeItem(storageKey);
            notif.classList.remove('show');
            notif.style.display = 'none';
        }, 2000);
    }
}

/**
 * Marca el formulario para notificación post-submit
 */
function markFormForNotification(formSelector, storageKey) {
    const form = document.querySelector(formSelector);
    if (form) {
        form.addEventListener('submit', function() {
            sessionStorage.setItem(storageKey, '1');
        });
    }
}

// Exponer funciones globalmente
window.initFileUpload = initFileUpload;
window.initDragDrop = initDragDrop;
window.VehicleSelector = VehicleSelector;
window.showFormNotification = showFormNotification;
window.initFormNotification = initFormNotification;
window.markFormForNotification = markFormForNotification;
