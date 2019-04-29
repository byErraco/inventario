function eventosForm() {
	$(document).on('click','.añadir', {}, function(e){
		obtenerForm(e)
	})
	if(typeof noObtenerForm === "undefined" || !noObtenerForm) obtenerForm()
}