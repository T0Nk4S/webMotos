// static/js/scripts.js
// Este archivo contiene todos los scripts de JavaScript para funcionalidades interactivas en el frontend.

document.addEventListener('DOMContentLoaded', () => {

    // === 1. Navbar Scroll Effect ===
    // Añade o quita la clase 'scrolled' al header dependiendo de la posición del scroll.
    const header = document.querySelector('.main-header');
    if (header) { // Asegura que el header existe antes de añadir el listener
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) { // Si el usuario ha bajado más de 50px
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // === 2. Mobile Menu Toggle ===
    // Controla la apertura y cierre del menú de navegación en dispositivos móviles.
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.getElementById('navbar-collapse'); // Usar getElementById para ID

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', () => {
            // Alterna la clase 'show' para mostrar/ocultar el menú
            navbarCollapse.classList.toggle('show');
            // Alterna el atributo aria-expanded para accesibilidad
            const expanded = navbarToggler.getAttribute('aria-expanded') === 'true' || false;
            navbarToggler.setAttribute('aria-expanded', !expanded);
        });

        // Cierra el menú móvil cuando se hace clic en un enlace (útil para Single Page Apps o navegación interna)
        navbarCollapse.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navbarCollapse.classList.remove('show');
                navbarToggler.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // === 3. Admin Secret Button Click Logic ===
    // Lógica para el botón "secreto" de acceso al panel de administrador (requiere múltiples clics).
    const adminSecretBtn = document.getElementById('admin-secret-btn');
    if (adminSecretBtn) {
        let clickCount = 0;
        let lastClickTime = 0;
        const clickThreshold = 5; // Número de clics necesarios
        const timeWindow = 1500; // Ventana de tiempo en ms (1.5 segundos)

        adminSecretBtn.addEventListener('click', () => {
            const currentTime = Date.now();

            // Reinicia el contador si ha pasado demasiado tiempo entre clics
            if (currentTime - lastClickTime > timeWindow) {
                clickCount = 0;
            }

            clickCount++;
            lastClickTime = currentTime;

            if (clickCount >= clickThreshold) {
                // Redirige a la página de login de admin.
                // adminLoginUrl debe ser definido globalmente en el HTML (ej. en layout.html)
                if (typeof adminLoginUrl !== 'undefined') {
                    window.location.href = adminLoginUrl;
                } else {
                    console.error("adminLoginUrl no está definido. No se puede redirigir.");
                    // Fallback o mostrar un mensaje al usuario
                    window.location.href = "/admin_login"; // Intenta una ruta por defecto
                }
                clickCount = 0; // Reinicia después de una redirección exitosa
            }
        });
    }

    // === 4. Interacción para los mensajes Flash (para que desaparezcan automáticamente) ===
    // Añade un temporizador para ocultar y eliminar los mensajes flash.
    const flashMessagesContainer = document.querySelector('.flash-messages');
    if (flashMessagesContainer) {
        const flashAlerts = flashMessagesContainer.querySelectorAll('.alert');
        flashAlerts.forEach(function(message) {
            setTimeout(function() {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease-out';
                message.addEventListener('transitionend', function() {
                    message.remove(); // Elimina el elemento del DOM después de la transición
                });
            }, 5000); // 5 segundos antes de empezar a desvanecer
        });
    }

    // === 5. Lógica para el cálculo automático en el formulario de factura (add_edit_invoice.html) ===
    // Calcula automáticamente el monto de impuesto y el total al cambiar subtotal o tasa.
    const invoiceForm = document.querySelector('form');
    // Verifica si es el formulario de factura basado en la acción (URL)
    if (invoiceForm && (invoiceForm.action.includes('/admin/invoices/add') || invoiceForm.action.includes('/admin/invoices/edit'))) {
        const subtotalField = invoiceForm.querySelector('#subtotal_amount');
        const taxRateField = invoiceForm.querySelector('#tax_rate');
        const taxAmountField = invoiceForm.querySelector('#tax_amount');
        const totalAmountField = invoiceForm.querySelector('#total_amount');

        function calculateInvoiceTotals() {
            let subtotal = parseFloat(subtotalField.value) || 0;
            let taxRate = parseFloat(taxRateField.value) || 0;

            let taxAmount = subtotal * (taxRate / 100);
            let totalAmount = subtotal + taxAmount;

            taxAmountField.value = taxAmount.toFixed(2); // Formatea a 2 decimales
            totalAmountField.value = totalAmount.toFixed(2); // Formatea a 2 decimales
        }

        // Añade listeners si los campos existen
        if (subtotalField) subtotalField.addEventListener('input', calculateInvoiceTotals);
        if (taxRateField) taxRateField.addEventListener('input', calculateInvoiceTotals);

        // Calcula los totales al cargar la página si ya hay valores
        calculateInvoiceTotals();
    }

    // === 6. Script para el carrusel Swiper (ejemplo para index.html) ===
    // Inicializa Swiper si el contenedor está presente.
    if (document.querySelector('.swiper-container')) {
        // Asegúrate de que la librería Swiper.js esté cargada antes de este script
        // <script src="https://unpkg.com/swiper/swiper-bundle.min.js"></script>
        var mySwiper = new Swiper('.swiper-container', {
            loop: true, // Carrusel infinito
            slidesPerView: 1,
            spaceBetween: 30, // Espacio entre slides
            grabCursor: true, // Cambia el cursor a "grab"
            autoplay: {
                delay: 9000, // Retraso de 9 segundos entre slides
                disableOnInteraction: false, // No deshabilita autoplay al interactuar
            },
            navigation: { // Flechas de navegación
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: { // Paginación por puntos
                el: '.swiper-pagination',
                clickable: true,
                type: 'bullets',
            },
            breakpoints: { // Configuración responsive
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            }
        });
    }

    // === 7. Script para el efecto de hover con cambio de color en logos de marcas (brands-section) ===
    // Añade un fondo dinámico a los logos de marcas al pasar el ratón.
    const logoItems = document.querySelectorAll('.logo-item');
    // Define una paleta de colores para el efecto
    const colors = [
        '#FF6347', '#FFD700', '#6A5ACD', '#32CD32', '#FF69B4',
        '#4682B4', '#DA70D6', '#BDB76B', '#00CED1', '#FFA07A'
    ];

    logoItems.forEach((item, index) => {
        const logoBg = document.createElement('div');
        logoBg.classList.add('logo-bg');
        item.prepend(logoBg); // Añade el div de fondo al principio del item

        item.addEventListener('mouseenter', () => {
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            // Usa una variable CSS personalizada para aplicar el color
            item.style.setProperty('--bg-color', randomColor);
        });
    });

    // === 8. Lógica para el botón "Limpiar Filtros" en catalogo_completo.html ===
    // Redirige al catálogo sin filtros al hacer clic.
    const clearFiltersButton = document.getElementById('clearFiltersBtn');
    if (clearFiltersButton) {
        clearFiltersButton.addEventListener('click', function() {
            // Asegúrate de que la URL para el catálogo completo sin filtros esté bien construida.
            // Si el nombre del blueprint es 'main_bp', usa 'main_bp.catalogo_completo'.
            if (typeof catalogoCompletoUrl !== 'undefined') {
                window.location.href = catalogoCompletoUrl;
            } else {
                console.error("catalogoCompletoUrl no está definido. No se puede limpiar filtros.");
                window.location.href = "/catalogo-completo"; // Fallback
            }
        });
    }
});