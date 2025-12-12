document.addEventListener('DOMContentLoaded', function() {
    
    const faqData = {
        categorias: [
            { id: 'general', nombre: 'Llantas', icon: 'fas fa-circle' },
            { id: 'compatibilidad', nombre: 'Compatibilidad', icon: 'fas fa-car' },
            { id: 'instalacion', nombre: 'Instalación', icon: 'fas fa-wrench' },
            { id: 'envios', nombre: 'Envíos', icon: 'fas fa-truck' },
            { id: 'pagos', nombre: 'Pagos', icon: 'fas fa-credit-card' },
            { id: 'garantias', nombre: 'Garantías', icon: 'fas fa-shield-alt' },
            { id: 'mantenimiento', nombre: 'Cuidados', icon: 'fas fa-tools' }
        ],
        preguntas: {
            general: [
                {
                    pregunta: '¿Qué diferencia hay entre una llanta de aleación y una de acero?',
                    respuesta: 'Las llantas de aleación son más ligeras, ofrecen mejor respuesta de la dirección y mejor disipación del calor del freno. Suelen ser más estéticas, pero también más delicadas frente a golpes fuertes. Las de acero son más pesadas, menos atractivas visualmente, pero más económicas y resistentes a maltrato extremo.'
                },
                {
                    pregunta: '¿Las llantas de aleación son compatibles con cualquier vehículo?',
                    respuesta: 'No. Cada vehículo tiene especificaciones de anclaje (PCD), centro de buje, diámetro, ancho y offset (ET). Es indispensable elegir una llanta que cumpla con estos parámetros para garantizar seguridad y un calce perfecto.'
                },
                {
                    pregunta: '¿Qué significan las medidas de las llantas (ej: 18x8 ET40 5x112)?',
                    respuesta: '<strong>18</strong>: diámetro de la llanta en pulgadas.<br><strong>8</strong>: ancho de la llanta en pulgadas.<br><strong>ET40</strong>: offset o desplazamiento (en mm).<br><strong>5x112</strong>: número de pernos (5) y distancia entre pernos (112 mm).'
                },
                {
                    pregunta: '¿Puedo montar llantas más grandes que las originales de fábrica?',
                    respuesta: 'Sí, pero siempre dentro de un rango seguro. Debes respetar:<br>• Diámetro total del neumático similar al original.<br>• Offset y ancho que no generen roces con amortiguadores o guardabarros.<br>Lo ideal es seguir las recomendaciones del fabricante del vehículo o de un especialista.'
                }
            ],
            compatibilidad: [
                {
                    pregunta: '¿Cómo sé qué llanta es compatible con mi auto?',
                    respuesta: 'Debes conocer al menos:<br>• Marca, modelo, año y versión de tu vehículo.<br>• Medidas originales (diámetro, ancho, PCD, ET).<br><br>En nuestro sitio puedes filtrar por vehículo o revisar la ficha técnica de cada llanta. Si tienes dudas, contáctanos antes de comprar.'
                },
                {
                    pregunta: '¿Qué es el PCD y por qué es importante?',
                    respuesta: 'El PCD (Pitch Circle Diameter) es el patrón de pernos: cuántos pernos tiene la rueda y el diámetro del círculo que forman. Debe coincidir exactamente con el de tu vehículo; si no, la llanta no montará correctamente.'
                },
                {
                    pregunta: '¿Qué es el offset (ET) y qué pasa si lo cambio?',
                    respuesta: 'El offset es la distancia entre el centro de la llanta y la superficie de montaje al buje.<br>• Un ET muy distinto al original puede hacer que la llanta quede muy "adentro" o muy "afuera".<br>• Cambios excesivos pueden provocar roces, desgaste irregular de neumáticos y esfuerzos adicionales en suspensión y rodamientos.'
                },
                {
                    pregunta: '¿Puedo usar centradores de buje?',
                    respuesta: 'Sí. Si el centro de la llanta es más grande que el buje de tu auto, se usan centradores para garantizar que la llanta quede perfectamente centrada. Es una práctica común y segura, siempre que se usen centradores de buena calidad.'
                }
            ],
            instalacion: [
                {
                    pregunta: '¿Las llantas se entregan con pernos/tuercas y centradores?',
                    respuesta: 'Depende del modelo. En la ficha del producto se indica qué incluye el kit (pernos, tuercas, centradores, tapas, etc.). Si no se incluye, puedes añadirlos como accesorios recomendados.'
                },
                {
                    pregunta: '¿Necesito alineación y balanceo al instalar llantas nuevas?',
                    respuesta: 'Sí, es altamente recomendable:<br>• <strong>Balanceo</strong> para evitar vibraciones a alta velocidad.<br>• <strong>Alineación</strong> para asegurar un desgaste parejo de los neumáticos y una dirección precisa.'
                },
                {
                    pregunta: '¿Puedo usar las mismas tuercas o pernos de la llanta original?',
                    respuesta: 'No siempre. Depende del tipo de asiento de la llanta (cónico, esférico, plano) y de la longitud necesaria. Verifica la compatibilidad o consulta con nuestro equipo antes de reutilizarlos.'
                }
            ],
            envios: [
                {
                    pregunta: '¿Realizan envíos a todo el país?',
                    respuesta: 'Sí, realizamos envíos a todo Chile. El costo y plazo de envío se calculan automáticamente al ingresar tu dirección en el checkout.'
                },
                {
                    pregunta: '¿Cuánto demora el despacho de mis llantas?',
                    respuesta: 'El plazo promedio es de 3-7 días hábiles desde la confirmación de pago, según tu zona. En fechas de alta demanda o zonas extremas, el plazo puede extenderse.'
                },
                {
                    pregunta: '¿Cómo vienen embaladas las llantas para el envío?',
                    respuesta: 'Cada llanta se envía protegida con caja o embalaje especial, esquineros y protección interna para minimizar riesgos de daño durante el transporte.'
                },
                {
                    pregunta: '¿Puedo retirar mi compra en tienda o bodega?',
                    respuesta: 'Sí. Contamos con opción de retiro en nuestra bodega, previa coordinación. Debes esperar el correo de confirmación de "pedido listo para retiro".'
                }
            ],
            pagos: [
                {
                    pregunta: '¿Qué medios de pago aceptan?',
                    respuesta: 'Aceptamos tarjetas de crédito y débito, transferencias bancarias y otros medios habilitados en la pasarela de pago (cuotas, billeteras digitales, etc.).'
                },
                {
                    pregunta: '¿Puedo solicitar factura a nombre de mi empresa?',
                    respuesta: 'Sí. Al momento de la compra, ingresa los datos de tu empresa en la sección de facturación. Emitiremos la factura electrónica una vez confirmado el pago.'
                },
                {
                    pregunta: '¿Es seguro comprar llantas en su sitio web?',
                    respuesta: 'Sí. Utilizamos pasarelas de pago certificadas y conexión cifrada (HTTPS) para proteger tus datos. Nunca almacenamos la información de tus tarjetas en nuestros servidores.'
                }
            ],
            garantias: [
                {
                    pregunta: '¿Las llantas tienen garantía?',
                    respuesta: 'Sí. Nuestras llantas cuentan con garantía contra defectos de fábrica por 12 meses desde la fecha de compra. La garantía no cubre daños por golpes, baches, choques, uso indebido o modificaciones.'
                },
                {
                    pregunta: '¿Qué hago si la llanta llega dañada o con golpes?',
                    respuesta: 'Debes revisar el paquete al recibirlo:<br>• Si ves daño evidente en el embalaje, deja constancia en la guía de despacho.<br>• Toma fotos y contáctanos dentro de las primeras 24–48 horas con tu número de pedido.<br>Evaluaremos el caso y coordinaremos cambio o reposición según corresponda.'
                },
                {
                    pregunta: '¿Puedo cambiar las llantas si no me gustó el diseño o la medida?',
                    respuesta: 'Sí, siempre que:<br>• No hayan sido montadas ni usadas.<br>• Vengan en su embalaje original y sin daños.<br>Los cambios están sujetos a revisión y a las condiciones de nuestra política de cambios y devoluciones. Los costos de envío pueden correr por cuenta del cliente.'
                }
            ],
            mantenimiento: [
                {
                    pregunta: '¿Cómo debo limpiar mis llantas de aleación?',
                    respuesta: 'Usa agua, jabón neutro y un paño o esponja suave. Evita productos muy agresivos, ácidos o cepillos metálicos, ya que pueden dañar la pintura y el barniz. No laves las llantas cuando están muy calientes.'
                },
                {
                    pregunta: '¿Las llantas de aleación se pueden reparar si se doblan o se fisuran?',
                    respuesta: 'Golpes leves que generan un pequeño "plano" o doblés en el labio muchas veces se pueden reparar en un taller especializado. Fisuras, quiebres o deformaciones graves pueden comprometer la seguridad, y en esos casos lo más responsable suele ser reemplazar la llanta.'
                },
                {
                    pregunta: '¿Las llantas de aleación aguantan uso en caminos malos o tierra?',
                    respuesta: 'Sí, pero son más sensibles a golpes fuertes que una llanta de acero. Recomendamos manejar con precaución en caminos muy dañados, evitar baches a alta velocidad y revisar periódicamente el estado de las llantas y neumáticos.'
                },
                {
                    pregunta: '¿Cada cuánto debo revisar el apriete de los pernos?',
                    respuesta: 'Se recomienda revisar el torque de los pernos:<br>• A los 50–100 km después de instalar llantas nuevas.<br>• Luego, según recomendaciones del fabricante o en cada servicio de mantención.'
                }
            ]
        }
    };

    // ============ ESTADO DEL CHATBOT ============
    let currentCategory = null;
    let conversationHistory = [];

    // ============ ELEMENTOS DEL DOM ============
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const categoriesContainer = document.getElementById('chatbot-categories');
    const questionsContainer = document.getElementById('chatbot-questions');
    const chatInput = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');

    if (!chatbotToggle || !chatbotContainer) return;

    // ============ FUNCIONES ============
    
    // Abrir/cerrar chatbot
    function toggleChatbot() {
        const isActive = chatbotContainer.classList.contains('active');
        chatbotContainer.classList.toggle('active');
        chatbotToggle.classList.toggle('active');
        
        if (!isActive && conversationHistory.length === 0) {
            setTimeout(() => {
                addBotMessage('¡Hola! 👋 Soy el asistente virtual de KRD Club. Estoy aquí para ayudarte con todas tus dudas sobre llantas de aleación.');
                setTimeout(() => {
                    addBotMessage('Selecciona una categoría para ver las preguntas frecuentes o escribe tu consulta.');
                }, 500);
            }, 300);
        }
    }

    function addBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot';
        messageDiv.innerHTML = text;
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
        conversationHistory.push({ type: 'bot', text });
    }

    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user';
        messageDiv.textContent = text;
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
        conversationHistory.push({ type: 'user', text });
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatbotMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    function scrollToBottom() {
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function renderCategories() {
        categoriesContainer.innerHTML = `
            <div class="categories-title">Categorías de Ayuda</div>
            <div class="category-buttons">
                ${faqData.categorias.map(cat => `
                    <button class="category-btn" data-category="${cat.id}">
                        <i class="${cat.icon}"></i> ${cat.nombre}
                    </button>
                `).join('')}
            </div>
        `;
        questionsContainer.innerHTML = '';
        questionsContainer.classList.add('hidden');
        categoriesContainer.classList.remove('hidden');
        currentCategory = null;

        categoriesContainer.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', () => selectCategory(btn.dataset.category));
        });
    }

    // Seleccionar categoría
    function selectCategory(categoryId) {
        currentCategory = categoryId;
        const categoria = faqData.categorias.find(c => c.id === categoryId);
        const preguntas = faqData.preguntas[categoryId];

        addUserMessage(categoria.nombre);
        
        showTypingIndicator();
        setTimeout(() => {
            hideTypingIndicator();
            addBotMessage(`Aquí tienes las preguntas frecuentes sobre <strong>${categoria.nombre}</strong>:`);
            
            questionsContainer.innerHTML = `
                <button class="back-btn" id="back-to-categories">
                    <i class="fas fa-arrow-left"></i> Volver a categorías
                </button>
                ${preguntas.map((p, index) => `
                    <button class="question-btn" data-category="${categoryId}" data-index="${index}">
                        ${p.pregunta}
                    </button>
                `).join('')}
            `;
            
            categoriesContainer.classList.add('hidden');
            questionsContainer.classList.remove('hidden');

            document.getElementById('back-to-categories').addEventListener('click', () => {
                renderCategories();
                addBotMessage('¿En qué otra categoría puedo ayudarte?');
            });

            questionsContainer.querySelectorAll('.question-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const cat = btn.dataset.category;
                    const idx = parseInt(btn.dataset.index);
                    answerQuestion(cat, idx);
                });
            });
        }, 600);
    }

    // Responder pregunta
    function answerQuestion(categoryId, index) {
        const pregunta = faqData.preguntas[categoryId][index];
        
        addUserMessage(pregunta.pregunta);
        
        showTypingIndicator();
        setTimeout(() => {
            hideTypingIndicator();
            addBotMessage(pregunta.respuesta);
            setTimeout(() => {
                addBotMessage('¿Tienes alguna otra pregunta? Puedes seleccionar otra categoría o escribir tu consulta.');
            }, 500);
        }, 800);
    }

    // Buscar en FAQ
    function searchFAQ(query) {
        const queryLower = query.toLowerCase();
        let bestMatch = null;
        let bestScore = 0;

        Object.keys(faqData.preguntas).forEach(category => {
            faqData.preguntas[category].forEach(item => {
                const preguntaLower = item.pregunta.toLowerCase();
                const respuestaLower = item.respuesta.toLowerCase();
                
                let score = 0;
                const words = queryLower.split(' ').filter(w => w.length > 2);
                
                words.forEach(word => {
                    if (preguntaLower.includes(word)) score += 3;
                    if (respuestaLower.includes(word)) score += 1;
                });

                if (score > bestScore) {
                    bestScore = score;
                    bestMatch = item;
                }
            });
        });

        return bestScore >= 3 ? bestMatch : null;
    }


    function processUserInput() {
        const text = chatInput.value.trim();
        if (!text) return;

        addUserMessage(text);
        chatInput.value = '';

        showTypingIndicator();
        setTimeout(() => {
            hideTypingIndicator();
            
            const match = searchFAQ(text);
            
            if (match) {
                addBotMessage(match.respuesta);
                setTimeout(() => {
                    addBotMessage('¿Te fue útil esta respuesta? Si tienes más preguntas, puedes seleccionar una categoría o seguir escribiendo.');
                }, 500);
            } else {
                addBotMessage('No encontré una respuesta exacta a tu consulta. Te sugiero:<br><br>• Seleccionar una categoría de las opciones disponibles<br>• Contactarnos directamente a <strong>info@krdclub.com</strong> o al <strong>+56 9 94837564</strong>');
            }
        }, 1000);
    }

    
    chatbotToggle.addEventListener('click', toggleChatbot);
    
    chatbotClose.addEventListener('click', () => {
        chatbotContainer.classList.remove('active');
        chatbotToggle.classList.remove('active');
    });

    sendBtn.addEventListener('click', processUserInput);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            processUserInput();
        }
    });
    renderCategories();

});
