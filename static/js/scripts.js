// static/js/scripts.js
// Este archivo contiene todos los scripts de JavaScript para funcionalidades interactivas en el frontend.

document.addEventListener('DOMContentLoaded', function() {
    // --- 1. Funcionalidad para el botón de toggle del menú de navegación (para móviles) ---
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }

    // --- 2. Interacción para los mensajes Flash (para que desaparezcan automáticamente) ---
    const flashMessagesContainer = document.querySelector('.flash-messages');
    if (flashMessagesContainer) {
        const flashAlerts = flashMessagesContainer.querySelectorAll('.alert');
        flashAlerts.forEach(function(message) {
            setTimeout(function() {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease-out';
                message.addEventListener('transitionend', function() {
                    message.remove();
                });
            }, 5000);
        });
    }

    // --- 3. Lógica para el cálculo automático en el formulario de factura ---
    const invoiceForm = document.querySelector('form');
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

            taxAmountField.value = taxAmount.toFixed(2);
            totalAmountField.value = totalAmount.toFixed(2);
        }

        if (subtotalField) subtotalField.addEventListener('input', calculateInvoiceTotals);
        if (taxRateField) taxRateField.addEventListener('input', calculateInvoiceTotals);

        calculateInvoiceTotals();
    }

    // --- 4. Script para el carrusel Swiper (ejemplo para index.html) ---
    if (document.querySelector('.swiper-container')) {
        var mySwiper = new Swiper('.swiper-container', {
            loop: true,
            slidesPerView: 1,
            spaceBetween: 30,
            grabCursor: true,
            autoplay: {
                delay: 90000,
                disableOnInteraction: false,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
                type: 'bullets',
            },
            breakpoints: {
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            }
        });
    }

    // --- 5. Script para el efecto de hover con cambio de color en logos de marcas (brands-section) ---
    const logoItems = document.querySelectorAll('.logo-item');
    const colors = [
        '#FF6347', '#FFD700', '#6A5ACD', '#32CD32', '#FF69B4',
        '#4682B4', '#DA70D6', '#BDB76B', '#00CED1', '#FFA07A'
    ];

    logoItems.forEach((item, index) => {
        const logoBg = document.createElement('div');
        logoBg.classList.add('logo-bg');
        item.prepend(logoBg);

        item.addEventListener('mouseenter', () => {
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            item.style.setProperty('--bg-color', randomColor);
        });
    });

    // --- 6. Script para el botón secreto del Admin ---
    const adminBtn = document.getElementById('admin-secret-btn');
    if (adminBtn) {
        // Este bloque ya no contiene lógica para ocultar el botón.
        // Su visibilidad y estilo son manejados exclusivamente por CSS.
        adminBtn.addEventListener('click', function() {
            window.location.href = adminLoginUrl;
        });
    }

    // --- 7. Lógica para el botón "Limpiar Filtros" en catalogo_completo.html ---
    const clearFiltersButton = document.getElementById('clearFiltersBtn');
    if (clearFiltersButton) {
        clearFiltersButton.addEventListener('click', function() {
            window.location.href = "{{ url_for('main_bp.catalogo_completo') }}";
        });
    }
});

// --- Script para el efecto de scroll en el header (se ejecuta con el evento 'scroll' de la ventana) ---
window.addEventListener('scroll', function() {
    const header = document.querySelector('.main-header');
    if (header) {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
});