
function calcularPrecioFinal(){
	var base = parseFloat($('#id_base_imponible').val()/(1-($('#id_margen_ganancia').val()/100)))
	$('#id_impuesto').val((base*($('#id_porcentaje_impuesto').val()/100)).toFixed(2))
	$('#id_precio_venta_publico').val((base+parseFloat($('#id_impuesto').val())).toFixed(2))
	$('#id_ganancia').val(($('#id_precio_venta_publico').val()-$('#id_impuesto').val()-$('#id_base_imponible').val()).toFixed(2))
}

function eventosForm() {
	$(document).on('change','#id_base_imponible', {}, function(e){
		calcularPrecioFinal()
	})
	$(document).on('change','#id_margen_ganancia', {}, function(e){
		calcularPrecioFinal()
	})
	$(document).on('change','#id_porcentaje_impuesto', {}, function(e){
		calcularPrecioFinal()
	})
	$(document).on('change','#id_precio_venta_publico', {}, function(e){
		$('#id_margen_ganancia').val(parseFloat(((($('#id_base_imponible').val()*(1+($('#id_porcentaje_impuesto').val()/100)))/$('#id_precio_venta_publico').val())-1)*(-100)).toFixed(1))
		var base = parseFloat($('#id_base_imponible').val()/(1-($('#id_margen_ganancia').val()/100)))
		$('#id_impuesto').val((base*($('#id_porcentaje_impuesto').val()/100)).toFixed(2))
		$('#id_ganancia').val(($('#id_precio_venta_publico').val()-$('#id_impuesto').val()-$('#id_base_imponible').val()).toFixed(2))
	})
}