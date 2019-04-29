
function eventosForm() {
	$(document).on('change','#id_almacen_produccion', {}, obtenerForm)
	$(document).on('change','#id_producto', {}, obtenerForm)
	$(document).on('change','#id_cantidad_produccion', {}, obtenerForm)
	$(document).on('click','.añadir', {}, function(e){
		obtenerForm(e)
	})
	$(document).on('keydown','#id_cantidad_produccion', {}, function(e){
		if(e.key == "ENTER") obtenerForm(e)
	})
	$(document).on('change', "[name$='codigo_lote']", {}, obtenerForm)
	obtenerForm()
}