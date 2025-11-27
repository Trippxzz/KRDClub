/**
 * Visor 360° con Sprites - Optimizado para 1 sola petición HTTP
 */
class Visor360Sprite {
    constructor(containerSelector, spriteData) {
        this.container = document.querySelector(containerSelector);
        this.spriteUrl = spriteData.url;
        this.cols = spriteData.cols;
        this.rows = spriteData.rows;
        this.totalFrames = spriteData.total;
        
        this.currentFrame = 0;
        this.isDragging = false;
        this.startX = 0;
        this.spriteImage = null;
        this.frameWidth = 0;
        this.frameHeight = 0;
        
        this.init();
    }
    
    async init() {
        this.mostrarCargando();
        await this.cargarSprite();
        this.setupCanvas();
        this.setupEventListeners();
        this.mostrarFrame(0);
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
    
    cargarSprite() {
        return new Promise((resolve, reject) => {
            this.spriteImage = new Image();
            this.spriteImage.onload = () => {
                this.frameWidth = this.spriteImage.width / this.cols;
                this.frameHeight = this.spriteImage.height / this.rows;
                console.log(`✅ Sprite 360 cargado: ${this.spriteImage.width}x${this.spriteImage.height}`);
                console.log(`📐 Frame: ${this.frameWidth}x${this.frameHeight}, Total: ${this.totalFrames} frames`);
                resolve();
            };
            this.spriteImage.onerror = () => {
                console.error('❌ Error cargando sprite');
                reject();
            };
            this.spriteImage.src = this.spriteUrl;
        });
    }
    
    setupCanvas() {
        const viewer = this.container.querySelector('.imagen-viewer');
        if (viewer) {
            viewer.innerHTML = '';
            
            this.canvas = document.createElement('canvas');
            this.canvas.width = this.frameWidth;
            this.canvas.height = this.frameHeight;
            this.canvas.classList.add('imagen-360');
            this.canvas.style.width = '100%';
            this.canvas.style.height = '100%';
            this.canvas.style.cursor = 'grab';
            
            this.ctx = this.canvas.getContext('2d');
            viewer.appendChild(this.canvas);
        }
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.startDrag(e));
        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('mouseup', () => this.stopDrag());
        
        this.canvas.addEventListener('touchstart', (e) => this.startDrag(e));
        document.addEventListener('touchmove', (e) => this.drag(e));
        document.addEventListener('touchend', () => this.stopDrag());
        
        this.canvas.addEventListener('dragstart', (e) => e.preventDefault());
    }
    
    startDrag(e) {
        this.isDragging = true;
        this.startX = e.pageX || (e.touches && e.touches[0].pageX);
        this.canvas.style.cursor = 'grabbing';
    }
    
    drag(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        
        const currentX = e.pageX || (e.touches && e.touches[0].pageX);
        const diff = currentX - this.startX;
        
        if (Math.abs(diff) > 8) {
            const direction = diff > 0 ? -1 : 1;
            this.rotarFrame(direction);
            this.startX = currentX;
        }
    }
    
    stopDrag() {
        this.isDragging = false;
        if (this.canvas) {
            this.canvas.style.cursor = 'grab';
        }
    }
    
    rotarFrame(direction) {
        let newFrame = this.currentFrame + direction;
        
        if (newFrame < 0) newFrame = this.totalFrames - 1;
        if (newFrame >= this.totalFrames) newFrame = 0;
        
        this.mostrarFrame(newFrame);
    }
    
    mostrarFrame(frameIndex) {
        this.currentFrame = frameIndex;
        
        const col = frameIndex % this.cols;
        const row = Math.floor(frameIndex / this.cols);
        
        const srcX = col * this.frameWidth;
        const srcY = row * this.frameHeight;
        
        this.ctx.clearRect(0, 0, this.frameWidth, this.frameHeight);
        this.ctx.drawImage(
            this.spriteImage,
            srcX, srcY, this.frameWidth, this.frameHeight,
            0, 0, this.frameWidth, this.frameHeight
        );
    }
}

/**
 * Visor 360° Legacy - Múltiples imágenes (compatibilidad con productos existentes)
 */
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
    // NUEVO: Sistema con sprites (1 sola petición HTTP)
    const spriteDataElement = document.getElementById('sprite-360-data');
    if (spriteDataElement && spriteDataElement.dataset.sprite) {
        const spriteData = JSON.parse(spriteDataElement.dataset.sprite);
        console.log('🚀 Inicializando visor 360 con SPRITE (1 petición):', spriteData);
        new Visor360Sprite('#visor-360-container', spriteData);
        return;
    }
    
    // LEGACY: Sistema con múltiples imágenes (compatibilidad)
    const dataElement = document.getElementById('imagenes-360');
    if (dataElement && dataElement.dataset.urls) {
        const imageUrls = JSON.parse(dataElement.dataset.urls);
        console.log('⚠️ Usando visor 360 legacy con', imageUrls.length, 'peticiones');
        const totalElement = document.getElementById('total-imagenes');
        if (totalElement) totalElement.textContent = imageUrls.length;
        
        new Visor360('#visor-360-container', imageUrls);
    }
});