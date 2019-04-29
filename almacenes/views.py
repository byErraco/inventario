from django.db.models import Q, F
from django.views import View
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.utils import formats
from django.utils.timezone import localtime

from inventario.views import CreateUpdateListView, ListView, CreateToDetailView, ReportView
from productos.models import Producto

from .models import Almacen, UnidadInventario, InventarioFisico
from .forms import AlmacenForm, PrecioUnidadInventarioForm, EliminarAlmacenForm, EliminarInventarioFisicoForm, InventarioFisicoForm, UnidadInventarioFisicoForm, UnidadInventarioFisicoBaseFormSet
from .filters import AlmacenFilter, UnidadInventarioFilter, InventarioFisicoFilter, UnidadInventarioFisicoFilter


class AlmacenesView(CreateUpdateListView):
	view_permission = 'almacenes.view_almacen'
	add_permission = 'almacenes.add_almacen'
	change_permission = 'almacenes.change_almacen'
	extra_context = {'modelo': 'almacen', 'titulo': 'Almacenes', 'titulo_form': 'Crear/Actualizar almacén', 'boton_form': 'Actualizar'}
	form_class = AlmacenForm
	updated_message = "El almacén fue actualizado"
	created_message = "El almacén fue creado"
	template_table = 'almacenes/tabla_body_almacen.html'
	paginate_by = 20
	delete_form_list = [EliminarAlmacenForm]
	filter_ = AlmacenFilter

	def get_object_forms(self, almacen):
		forms = {}

		if self.request.user.has_perm('almacenes.delete_almacen'):
			if not almacen.unidades_inventario_actuales.exists() and not almacen.traslados_pendientes.exists():
				forms['Eliminar'] = EliminarAlmacenForm(initial={'object_id':almacen.id}) 
		return forms

	def get_object(self, request):
	    try:
	    	tienda = request.POST['tienda']
	    	if tienda == '':
	    		return Almacen.objects.actuales().get(tienda__isnull=True, nombre=request.POST['nombre'])
	    	return Almacen.objects.actuales().get(tienda=tienda, nombre=request.POST['nombre'])
	    except:
	        return None 
			

class UnidadesInventarioView(CreateUpdateListView):
	view_permission = 'almacenes.view_unidadinventario'
	add_permission = 'almacenes.add_preciounidadinventario'
	change_permission = 'almacenes.change_preciounidadinventario'
	template_table = 'almacenes/tabla_body_unidad_inventario.html'
	paginate_by = 10
	extra_context = {'modelo': 'unidad_inventario', 'titulo': 'Lista de productos en inventario', 'titulo_form': 'Crear/Actualizar precio', 'boton_form': 'Actualizar'}
	form_class = PrecioUnidadInventarioForm
	updated_message = "El precio fue actualizado"
	created_message = "El precio fue creado"
	filter_ = UnidadInventarioFilter


class InventariosFisicosView(ListView):
	permission_required = 'almacenes.view_inventariofisico'
	add_permission = 'almacenes.add_inventariofisico'
	change_permission = 'almacenes.change_inventariofisico'
	extra_context = {'modelo': 'inventario_fisico', 'titulo': 'Lista de inventarios físicos', 'can_add': True}
	template_name = 'base_lista.html'
	template_table = 'almacenes/tabla_body_inventario_fisico.html'
	paginate_by = 25
	delete_form_list = [EliminarInventarioFisicoForm]
	filter_ = InventarioFisicoFilter
	
	def get_object_forms(self, inventario_fisico):
		forms = {}

		if self.request.user.has_almacen_perm(inventario_fisico.unidades_inventario_fisico.actuales()[0].unidad_inventario.control_stock.almacen, 'delete_inventariofisico'):
			forms['Eliminar'] = EliminarInventarioFisicoForm(initial={'object_id':inventario_fisico.id}) 
		return forms


class CrearInventarioFisicoView(View):
	template_name = 'base_lista_crear.html'
	permission_required = 'almacenes.add_inventariofisico'
	extra_context = { 'titulo_form': 'crear inventario físico', 'titulo': 'Nuevo inventario físico', 'modelo': 'inventario_fisico', 'form_no_ajax': True}

	def get(self, request, *args, **kwargs):
		forms = []
		forms.append(InventarioFisicoForm())

		UnidadInventarioFisicoFormset = formset_factory(form=UnidadInventarioFisicoForm, extra=0, can_delete=False, formset=UnidadInventarioFisicoBaseFormSet)

		formset = UnidadInventarioFisicoFormset()

		forms.append(formset)

		self.extra_context.update({'forms': forms})
		return render(request, self.template_name, self.extra_context)
	

	def post(self, request, *args, **kwargs):
	    context = { 'titulo_form': 'crear inventario físico' }

	    form = InventarioFisicoForm(request.POST or None)

	    UnidadInventarioFisicoFormset = formset_factory(form=UnidadInventarioFisicoForm, extra=0, can_delete=False, formset=UnidadInventarioFisicoBaseFormSet)

	    prefix = UnidadInventarioFisicoFormset().prefix
	    totalForms = request.POST.get(prefix+'-'+'TOTAL_FORMS')
	    initial = []
	    if totalForms:
	    	for i in range(int(totalForms)):
	    		subformPrefix = prefix+'-'+str(i)+'-'
	    		subformInitial = {key.replace(subformPrefix, ''):value for key, value in request.POST.items() if subformPrefix in key}
	    		initial.append(subformInitial)

	    formset = UnidadInventarioFisicoFormset(request.POST, initial=initial)
	 
	    form_valid = form.is_valid()
	    formset_valid = formset.is_valid()
	    if form_valid and formset_valid:
	    	inventario_fisico = form.save()
	    	almacen = Almacen.objects.get(pk=request.POST.get('almacen'))

	    	formset.save(inventario_fisico, almacen)
	    	return redirect('almacenes:detalle_inventario_fisico', id=inventario_fisico.id)

	    self.extra_context.update({'forms': [form, formset], 'no_obtener_form':True})
	    return render(request, self.template_name, self.extra_context)



class InventarioFisicoFormView(View):
	def post(self, request, *args, **kwargs):
	    if request.is_ajax():
	        forms = []
	        forms.append(InventarioFisicoForm(initial = dict(request.POST.items())))

	        changed_data = request.POST.get('changed_data')

	        if changed_data:
	        	extra = 1
	        else:
	        	extra = 0

	        UnidadInventarioFisicoFormset = formset_factory(form=UnidadInventarioFisicoForm, extra=extra, can_delete=False, formset=UnidadInventarioFisicoBaseFormSet)
	        
	        prefix = UnidadInventarioFisicoFormset().prefix
	        totalForms = request.POST.get(prefix+'-'+'TOTAL_FORMS')
	        initial = []
	        if totalForms:
	            for i in range(int(totalForms)):
	                subformPrefix = prefix+'-'+str(i)+'-'
	                subformInitial = {key.replace(subformPrefix, ''):value for key, value in request.POST.items() if subformPrefix in key}
	                initial.append(subformInitial)

	        formset = UnidadInventarioFisicoFormset(initial=initial)

	        if changed_data:
	        	if int(request.POST.get('form-TOTAL_FORMS')) > 0:
	        		formset_valid = UnidadInventarioFisicoFormset(request.POST, initial=initial)
	        		if not formset_valid.is_valid():
	        			formset = formset_valid
	        	
	        
	        forms.append(formset)
	        return render(request, 'forms.html', {'forms': forms, 'titulo_form': 'crear inventario físico'})
	   
	    raise Http404


class DetalleInventarioFisicoView(ListView):
	permission_required = 'almacenes.view_inventariofisico'
	extra_context = {'modelo': 'unidad_inventario_fisico'}
	template_name = 'base_lista.html'
	template_table = 'almacenes/tabla_body_unidad_inventario_fisico.html'
	paginate_by = 25
	filter_ = UnidadInventarioFisicoFilter

	def get(self, request, id):
		inventario_fisico = InventarioFisico.objects.get(id=id)
		self.extra_context['titulo'] = 'Usuario: {}\nAlmacén: {}\nFecha: {}'.format(inventario_fisico.usuario_creacion, inventario_fisico.almacen, formats.date_format(localtime(inventario_fisico.fecha_creacion), "d-m-Y g:i a"))
		return super().get(request, inventario_fisico=id)


class InventarioFisicoReportView(ReportView):
    filename = 'reporte_inventario_fisico'
    title = 'Reporte de inventario físico'

    def append_objects(self, request, ws, **kwargs):
    	inventario_fisico = InventarioFisico.objects.get(id=kwargs['id'])

    	ws.append(['Usuario: '+str(inventario_fisico.usuario_creacion)])
    	ws.append(['Almacén: '+str(inventario_fisico.almacen)])
    	ws.append(['Fecha de creación: '+localtime(inventario_fisico.fecha_creacion).strftime('%m-%d-%Y %I:%M %p')])
    	ws.append([])

    	ws.append(['Producto', 'Código de lote', 'Cantidad física', 'Cantidad en sistema', 'Unidad'])

    	object_list = inventario_fisico.unidades_inventario_fisico.actuales().con_cantidad_sistema()

    	for obj in object_list:
    	    max_row = ws.max_row+1

    	    ws.cell(row=max_row, column=1).value = str(obj.unidad_inventario.control_stock.producto)
    	    if obj.unidad_inventario.lote_produccion:
    	        ws.cell(row=max_row, column=2).value = str(obj.unidad_inventario.lote_produccion.codigo)

    	    ws.cell(row=max_row, column=3).value = obj.cantidad_producto

    	    ws.cell(row=max_row, column=4).value = obj.cantidad_sistema

    	    unidad = obj.unidad_inventario.control_stock.producto.unidad

    	    if unidad:
    	    	ws.cell(row=max_row, column=5).value = str(unidad)
    	    else:
    	    	ws.cell(row=max_row, column=5).value = 'Unidad'


        