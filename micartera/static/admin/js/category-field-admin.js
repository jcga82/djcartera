jQuery(document).ready(function ($) {
    (function ($) {
        $(function() {
            var selectField = $('#id_estrategia');
            var verified = $('#id_dividendo_desde');
            var fechas_dividendo = $('#id_fechas_dividendo');
            
            var fechas_dividendo = $('#id_fechas_dividendo');
    
            function toggleVerified(value) {
                //value != 'Dividendos' ? verified.show() : verified.hide();
                if (value == 'Dividendos') {
                    verified.show();
                    fechas_dividendo.show();
                }else {
                    verified.hide();
                    fechas_dividendo.hide();
                }
                    
            }
    
            // show/hide on load based on pervious value of selectField
            toggleVerified(selectField.val());
    
            // show/hide on change
            selectField.change(function() {
                toggleVerified($(this).val());
            });
        });
    })(django.jQuery);
});