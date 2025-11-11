// Script para habilitar/deshabilitar campos en el Admin de Django
(function() {
    'use strict';
    
    // Esperar a que el DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', function() {
        const metodoSelect = document.getElementById('id_metodo_ingreso');
        const montoInput = document.getElementById('id_monto');
        const factorInput = document.getElementById('id_factor');
        
        if (!metodoSelect || !montoInput || !factorInput) {
            return; // Salir si no existen los elementos
        }
        
        function actualizarCampos() {
            const metodo = metodoSelect.value;
            
            if (metodo === 'MONTO') {
                // Habilitar monto, deshabilitar factor
                montoInput.disabled = false;
                montoInput.parentElement.style.opacity = '1';
                factorInput.disabled = true;
                factorInput.parentElement.style.opacity = '0.5';
                factorInput.value = '';  // Limpiar el campo deshabilitado
            } else if (metodo === 'FACTOR') {
                // Habilitar factor, deshabilitar monto
                factorInput.disabled = false;
                factorInput.parentElement.style.opacity = '1';
                montoInput.disabled = true;
                montoInput.parentElement.style.opacity = '0.5';
                montoInput.value = '';  // Limpiar el campo deshabilitado
            }
        }
        
        // Ejecutar al cargar la página
        actualizarCampos();
        
        // Ejecutar cada vez que cambie la selección
        metodoSelect.addEventListener('change', actualizarCampos);
    });
})();
