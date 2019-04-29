
function eventosForm() {
	$(document).on('change','#id_categorias', {}, obtenerForm)
	$(document).on('change','#id_producto', {}, obtenerForm)
	$(document).on('change','#id_codigo_lote', {}, obtenerForm)
	$(document).on('click','.añadir', {}, function(e){
		cloneMore($(this).parent().parent().find(".formset-form:last"), $(this).attr('name').slice(0, $(this).attr('name').indexOf("-")))
	})
	obtenerForm()
}