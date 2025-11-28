/**
 * KRD Club - Carrusel de Productos Destacados
 * Carrusel responsive con auto-play y controles de navegación
 */

document.addEventListener('DOMContentLoaded', function() {
    const carousel = {
        track: document.getElementById('carousel-track'),
        prevBtn: document.getElementById('carousel-prev'),
        nextBtn: document.getElementById('carousel-next'),
        indicatorsContainer: document.getElementById('carousel-indicators'),
        slides: null,
        currentIndex: 0,
        slidesPerView: 3,
        totalSlides: 0,
        maxIndex: 0,
        autoPlayInterval: null,
        autoPlayDelay: 5000, // 5 segundos
        isAnimating: false,

        init() {
            if (!this.track) return;
            
            this.slides = this.track.querySelectorAll('.carousel-slide');
            this.totalSlides = this.slides.length;
            
            if (this.totalSlides === 0) return;

            this.updateSlidesPerView();
            this.createIndicators();
            this.updateCarousel();
            this.bindEvents();
            this.startAutoPlay();
        },

        updateSlidesPerView() {
            const width = window.innerWidth;
            if (width < 768) {
                this.slidesPerView = 1;
            } else if (width < 1024) {
                this.slidesPerView = 2;
            } else {
                this.slidesPerView = 3;
            }
            this.maxIndex = Math.max(0, this.totalSlides - this.slidesPerView);
        },

        createIndicators() {
            if (!this.indicatorsContainer) return;
            
            this.indicatorsContainer.innerHTML = '';
            const numIndicators = this.maxIndex + 1;
            
            for (let i = 0; i < numIndicators; i++) {
                const indicator = document.createElement('button');
                indicator.classList.add('carousel-indicator');
                indicator.setAttribute('aria-label', `Ir a slide ${i + 1}`);
                indicator.dataset.index = i;
                
                if (i === 0) {
                    indicator.classList.add('active');
                }
                
                indicator.addEventListener('click', () => {
                    this.goToSlide(i);
                });
                
                this.indicatorsContainer.appendChild(indicator);
            }
        },

        updateIndicators() {
            if (!this.indicatorsContainer) return;
            
            const indicators = this.indicatorsContainer.querySelectorAll('.carousel-indicator');
            indicators.forEach((indicator, index) => {
                indicator.classList.toggle('active', index === this.currentIndex);
            });
        },

        updateCarousel() {
            if (this.isAnimating) return;
            
            const slideWidth = 100 / this.slidesPerView;
            const offset = -this.currentIndex * slideWidth;
            
            this.track.style.transform = `translateX(${offset}%)`;
            
            // Actualizar estado de botones
            if (this.prevBtn) {
                this.prevBtn.disabled = this.currentIndex === 0;
            }
            if (this.nextBtn) {
                this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
            }
            
            this.updateIndicators();
        },

        goToSlide(index) {
            if (this.isAnimating) return;
            
            this.currentIndex = Math.max(0, Math.min(index, this.maxIndex));
            this.updateCarousel();
            this.resetAutoPlay();
        },

        nextSlide() {
            if (this.currentIndex < this.maxIndex) {
                this.goToSlide(this.currentIndex + 1);
            } else {
                // Volver al inicio para loop infinito
                this.goToSlide(0);
            }
        },

        prevSlide() {
            if (this.currentIndex > 0) {
                this.goToSlide(this.currentIndex - 1);
            } else {
                // Ir al final para loop infinito
                this.goToSlide(this.maxIndex);
            }
        },

        bindEvents() {
            // Botones de navegación
            if (this.prevBtn) {
                this.prevBtn.addEventListener('click', () => this.prevSlide());
            }
            if (this.nextBtn) {
                this.nextBtn.addEventListener('click', () => this.nextSlide());
            }

            // Resize
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    this.updateSlidesPerView();
                    this.createIndicators();
                    if (this.currentIndex > this.maxIndex) {
                        this.currentIndex = this.maxIndex;
                    }
                    this.updateCarousel();
                }, 250);
            });

            // Pausar autoplay al hover
            if (this.track) {
                this.track.addEventListener('mouseenter', () => this.stopAutoPlay());
                this.track.addEventListener('mouseleave', () => this.startAutoPlay());
            }

            // Touch/Swipe support
            this.initTouchEvents();

            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') {
                    this.prevSlide();
                } else if (e.key === 'ArrowRight') {
                    this.nextSlide();
                }
            });
        },

        initTouchEvents() {
            let startX = 0;
            let endX = 0;
            const threshold = 50;

            this.track.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                this.stopAutoPlay();
            }, { passive: true });

            this.track.addEventListener('touchmove', (e) => {
                endX = e.touches[0].clientX;
            }, { passive: true });

            this.track.addEventListener('touchend', () => {
                const diff = startX - endX;
                
                if (Math.abs(diff) > threshold) {
                    if (diff > 0) {
                        this.nextSlide();
                    } else {
                        this.prevSlide();
                    }
                }
                
                this.startAutoPlay();
            });
        },

        startAutoPlay() {
            this.stopAutoPlay();
            this.autoPlayInterval = setInterval(() => {
                this.nextSlide();
            }, this.autoPlayDelay);
        },

        stopAutoPlay() {
            if (this.autoPlayInterval) {
                clearInterval(this.autoPlayInterval);
                this.autoPlayInterval = null;
            }
        },

        resetAutoPlay() {
            this.stopAutoPlay();
            this.startAutoPlay();
        }
    };

    // Inicializar el carrusel
    carousel.init();
});
