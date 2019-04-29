
function eventosForm() {
	$(document).on('change','#id_categorias', {}, obtenerForm)
	$(document).on('change','#id_almacen_origen', {}, obtenerForm)
	$(document).on('change','#id_producto', {}, obtenerForm)
	$(document).on('change','#id_codigo_lote', {}, obtenerForm)
	$(document).on('submit','.confirmar-form', {}, function(e){
		event.preventDefault();

		$.ajax({
		    url: urlProcesar,
		    method: "POST",
		    data: obtenerDataForm($(this).attr("id")),
		    success: function(data){
		        buscar()
		    },
		    error: function(error){
		        console.log(error)
		    }
		});
	})
	obtenerForm()
}