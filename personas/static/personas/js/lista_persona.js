"use strict";


function obtenerDataForm() {
	var data = {}

	data.nombre = $("#id_nombre").val()
	data.apellido = $("#id_apellido").val()
	data.tipo = $("#id_tipo").val()
	data.numero_identificacion = $("#id_numero_identificacion").val()
	data.direccion = $("#id_direccion").val()
	data.email = $("#id_email").val()
	data.telefono = $("#id_telefono").val()
	data.fecha_creacion = $("#id_fecha_creacion").val()
	data.fecha_ultima_modificacion = $("#id_fecha_ultima_modificacion").val()

	return data
}