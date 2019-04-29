
function eventosForm() {
	$(document).on('change','#id_categorias', {}, obtenerForm)
	$(document).on('change','#id_almacen', {}, obtenerForm)
	$(document).on('change','#id_producto', {}, obtenerForm)
	$(document).on('change','#id_codigo_lote', {}, obtenerForm)
	obtenerForm()
}