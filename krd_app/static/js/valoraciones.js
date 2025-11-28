/**
 * VALORACIONES.JS - KRD Club
 * Sistema interactivo de valoraciones con estrellas
 */

document.addEventListener('DOMContentLoaded', function() {
    
    const ratingTexts = {
        1: 'Malo',
        2: 'Regular',
        3: 'Bueno',
        4: 'Muy Bueno',
        5: 'Excelente'
    };

    // Rating General
    const ratingGeneral = document.getElementById('rating-general');
    const inputEstrellas = document.getElementById('estrellas');
    const ratingText = document.getElementById('rating-text');
    
    if (ratingGeneral) {
        const stars = ratingGeneral.querySelectorAll('.star');
        let currentRating = 5;
        
        updateStars(stars, 5);
        
        stars.forEach((star, index) => {
            star.addEventListener('mouseenter', () => {
                highlightStars(stars, index + 1);
            });
            
            star.addEventListener('click', () => {
                currentRating = index + 1;
                inputEstrellas.value = currentRating;
                updateStars(stars, currentRating);
                
                if (ratingText) {
                    ratingText.textContent = ratingTexts[currentRating];
                    ratingText.className = 'text-center text-gray-500 text-sm mt-3';
                }
            });
        });
        
        ratingGeneral.addEventListener('mouseleave', () => {
            updateStars(stars, currentRating);
        });
    }

    // Funciones auxiliares
    function updateStars(stars, rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.remove('empty');
                star.classList.add('active');
            } else {
                star.classList.add('empty');
                star.classList.remove('active');
            }
        });
    }
    
    function highlightStars(stars, rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.remove('empty');
            } else {
                star.classList.add('empty');
            }
        });
    }

    // Contador de caracteres
    const comentario = document.getElementById('comentario');
    const charCount = document.getElementById('char-count');
    
    if (comentario && charCount) {
        comentario.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });
    }

});
