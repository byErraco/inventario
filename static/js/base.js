"use strict";


function clickPaginador(){
    buscar($(this).val());
}


function crearPaginador(){
    $("#primera").click(clickPaginador);
    $("#anterior").click(clickPaginador);
    $("#actual").click(clickPaginador);
    $("#siguiente").click(clickPaginador);
    $("#ultima").click(clickPaginador);
}


function actualizarPaginador(paginaActual, ultimaPagina){
    paginaActual = parseInt(paginaActual);

    var paginaAnterior = paginaActual-1;
    var paginaSiguiente = paginaActual+1;

    $("#anterior").prop("value", paginaAnterior);
    $("#anterior").html(paginaAnterior);
    $("#actual").prop("value", paginaActual);
    $("#actual").html(paginaActual);
    $("#siguiente").prop("value", paginaSiguiente);
    $("#siguiente").html(paginaSiguiente);
    $("#ultima").prop("value", ultimaPagina);

    if(paginaAnterior > 1){
        $("#anterior").parent().show();
    }
    else {
        $("#anterior").parent().hide();
    }

    if(paginaSiguiente < ultimaPagina){
        $("#siguiente").parent().show();
    }
    else {
        $("#siguiente").parent().hide();
    }

    if(paginaActual > 1){
        $("#primera").parent().show();
    }
    else {
        $("#primera").parent().hide();
    }

    if(paginaActual < ultimaPagina){
        $("#ultima").parent().show();
    }
    else {
        $("#ultima").parent().hide();
    }
}


function csrfSafeMethod(method) {
    // These HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


function buscar(pagina=1, cambiar_form=false){
    var dataOriginal = obtenerDataForm("id_filter_form")

    if(typeof urlLista != "undefined" && urlLista != null){
        $.ajax({
            url: urlLista+pagina,
            method: "GET",
            data: dataOriginal,
            success: function(data){
                $("#tabla-body").replaceWith(data.results)

                if(cambiar_form){
                    $("#id_filter_form").empty()
                    $("#id_filter_form").append(data.filter_form)

                    $("#id_filter_form select[multiple]").each(function(){
                        $(this).val(dataOriginal[$(this).attr('name')])
                    })
                }

                actualizarPaginador(pagina, data.page_count);

                if($("#tabla-body tr").length > 0){
                    $("#resultados").show();
                    $("#ninguno").hide();
                }
                else {
                    $("#resultados").hide();
                    $("#ninguno").show();
                }
            },
            error: function(error){
                console.log(error)
            }
        });
    }
}

function cloneMore(node, type) {
    var max = parseInt($('#id_' + type + '-MAX_NUM_FORMS').val());
    var total = parseInt($('#id_' + type + '-TOTAL_FORMS').val());

    if(total < max){
        var newElement = node.clone(true);
        newElement.find(':input').each(function() {
            var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        });
        newElement.find('label').each(function() {
            var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
            $(this).attr('for', newFor);
        });
        total++;
        $('#id_' + type + '-TOTAL_FORMS').val(total);
        node.after(newElement);
    }
}


function obtenerDataForm(form_id="form") {
    var nombre_boton = $("#"+form_id+" input[type=submit]").attr("name")
    var data = {}

    if(typeof nombre_boton != 'undefined'){
        data[nombre_boton] = nombre_boton
    }
    
    $("#"+form_id+" input:not([type=submit])").each(function(){
        if($(this).attr("type") != "checkbox") data[$(this).attr("name")] = $(this).val()
        else if($(this).prop("checked")) data[$(this).attr("name")] = $(this).val()
    })
    $("#"+form_id+" select").each(function(){
        data[$(this).attr('name')] = $(this).val()
    })

    return data
}


function obtenerForm(event) {
    var dataOriginal = obtenerDataForm()
    
    if(typeof event != "undefined"){
        dataOriginal.changed_data = event.target.name
    }

    $.ajax({
        url: urlForm,
        method: "POST",
        data: dataOriginal,
        success: function(data){
            $("#data-form").replaceWith(data)

            $("#data-form select[multiple]").each(function(){
                $(this).val(dataOriginal[$(this).attr('name')])
            })
        },
        error: function(error){
            console.log(error)
        }
    })
}


function crearFormulario(){
    $("#form").submit(function(event){
        event.preventDefault();
        
        $.ajax({
            url: urlProcesar,
            method: "POST",
            data: obtenerDataForm(),
            success: function(data){
                $("#data-form").replaceWith(data)
                $("#data-form input").keypress(function(){
                    $("#success").remove() 
                })
                $("#data-form select").change(function(){
                    $("#success").remove() 
                })
                buscar()
            },
            error: function(error){
                console.log(error)
            }
        });
    });
}


$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function eventosLista(){
    $(document).on('submit','.eliminar-form', {}, function(e){
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

    $("#id_filter_form").on('keyup','input', {}, function(e){
        buscar()
    })
    $("#id_filter_form").on('change','input[type!=text]', {}, function(e){
        buscar(1, true)
    })
    $("#id_filter_form").on('change','select', {}, function(e){
        buscar(1, true)
    })
}


function agregarCero(num) {
    return (num < 10 ? "0" : "" ) + num;
}


function updateClock() {
    var currentTime = new Date();
    var currentDate = agregarCero(currentTime.getDate());
    var currentMonth = agregarCero(currentTime.getMonth());
    var currentFullYear = currentTime.getFullYear();
    var currentHours = agregarCero(currentTime.getHours());
    var currentMinutes = agregarCero(currentTime.getMinutes());
    
    $("#fecha").html("Fecha: "+currentDate+"-"+currentMonth+"-"+currentFullYear+" Hora: "+currentHours+":"+currentMinutes);
}


$(document).ready(function() {
	crearPaginador();
	buscar();
    if(typeof eventosForm === 'function') {
        eventosForm();
    } 
    eventosLista();
    if($("#form").length && (typeof noAjax === "undefined" || !noAjax)) crearFormulario();
    if($("#fecha").length) {
        updateClock(); 
        setInterval(updateClock, 1000);
    }
});