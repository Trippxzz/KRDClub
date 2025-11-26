class Visor360 {
    constructor(containerSelector, imageUrls) {
        this.container = document.querySelector(containerSelector);
        this.imageUrls = imageUrls;
        this.currentIndex = 0;
        this.images = [];
        this.isLoaded = false;
        this.isDragging = false;
        this.startX = 0;
        this.imagenesCargadas = 0;
        
        this.init();
    }
    
    async init() {
        this.mostrarCargando();
        await this.cargarImagenesIniciales();
        this.cargarImagenesRestantes();
        this.setupEventListeners();
        this.mostrarImagen(0);
        this.ocultarCargando();
    }
    
    mostrarCargando() {
        const spinner = this.container.querySelector('.loading-spinner');
        if (spinner) spinner.style.display = 'block';
    }
    
    ocultarCargando() {
        const spinner = this.container.querySelector('.loading-spinner');
        if (spinner) spinner.style.display = 'none';
    }
    
    async cargarImagenesIniciales() {
        const primerasImagenes = [0, 9, 18, 27];
        const promesas = primerasImagenes.map(i => this.precargarImagen(i));
        await Promise.all(promesas);
    }
    
    cargarImagenesRestantes() {
        this.imageUrls.forEach((url, index) => {
            if (![0, 9, 18, 27].includes(index)) {
                setTimeout(() => this.precargarImagen(index), index * 50);
            }
        });
    }
    
    precargarImagen(index) {
        return new Promise((resolve) => {
            if (this.images[index]) {
                resolve();
                return;
            }
            
            const img = new Image();
            img.onload = () => {
                this.images[index] = img;
                this.imagenesCargadas++;
                this.actualizarIndicador();
                resolve();
            };
            img.src = this.imageUrls[index];
        });
    }
    
    actualizarIndicador() {
        const elem = document.getElementById('imagenes-cargadas');
        if (elem) elem.textContent = this.imagenesCargadas;
    }
    
    setupEventListeners() {
        this.container.addEventListener('mousedown', (e) => this.startDrag(e));
        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('mouseup', () => this.stopDrag());
        
        this.container.addEventListener('touchstart', (e) => this.startDrag(e));
        document.addEventListener('touchmove', (e) => this.drag(e));
        document.addEventListener('touchend', () => this.stopDrag());
    }
    
    startDrag(e) {
        this.isDragging = true;
        this.startX = e.pageX || e.touches[0].pageX;
        this.container.style.cursor = 'grabbing';
    }
    
    drag(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        
        const currentX = e.pageX || (e.touches && e.touches[0].pageX);
        const diff = currentX - this.startX;
        
        if (Math.abs(diff) > 10) {
            const direction = diff > 0 ? -1 : 1;
            this.rotarImagen(direction);
            this.startX = currentX;
        }
    }
    
    stopDrag() {
        this.isDragging = false;
        this.container.style.cursor = 'grab';
    }
    
    rotarImagen(direction) {
        let newIndex = this.currentIndex + direction;
        
        if (newIndex < 0) newIndex = this.imageUrls.length - 1;
        if (newIndex >= this.imageUrls.length) newIndex = 0;
        
        this.mostrarImagen(newIndex);
    }
    
    mostrarImagen(index) {
        if (!this.images[index]) {
            return;
        }
        
        this.currentIndex = index;
        const viewer = this.container.querySelector('.imagen-viewer');
        if (viewer) {
            viewer.innerHTML = '';
            this.images[index].classList.add('imagen-360');
            viewer.appendChild(this.images[index]);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('imagenes-360');
    if (dataElement) {
        const imageUrls = JSON.parse(dataElement.dataset.urls);
        const totalElement = document.getElementById('total-imagenes');
        if (totalElement) totalElement.textContent = imageUrls.length;
        
        new Visor360('#visor-360-container', imageUrls);
    }
});