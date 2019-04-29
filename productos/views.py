from django.shortcuts import render, redirect

from collections import OrderedDict

from inventario.views import CreateToDetailView, ListView, CreateUpdateListView, DetailFormsView
from almacenes.models import UnidadInventario, Almacen

from .forms import *
from .filters import ProductoFilter, CategoriaProductoFilter, UnidadFilter

# Create your views here.


class CrearProductoView(CreateToDetailView):
    form_class = ProductoForm
    template_name = 'productos/base_detalle.html'
    permission_required = 'productos.add_producto'
    change_permission = 'productos.change_producto'
    extra_context = {'titulo': 'Nuevo producto', 'modelo': 'Producto'}

    def get(self, request, *args, **kwargs):
    	if request.user.has_perm('productos.add_unidad'):
    		self.extra_context.update({'forms': {'nueva unidad': UnidadForm}})

    	return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
    	if request.user.has_perm('productos.add_unidad') and UnidadForm.nombre_form in request.POST:
    		unidad_form = UnidadForm(request.POST or None)

    		if unidad_form.is_valid():
    			unidad_form.save()

    		return render(request, self.template_name, {'form': ProductoForm, 'forms': {'nueva unidad': unidad_form}, **self.extra_context})
    	else:
    		return super().post(request, *args, **kwargs)


class CrearCategoriaProductoView(CreateToDetailView):
    form_class = CategoriaProductoForm
    template_name = 'productos/base_detalle.html'
    permission_required = 'productos.add_categoriaproducto'
    change_permission = 'productos.change_categoriaproducto'
    extra_context = {'titulo': 'Nueva categoría', 'modelo': 'Categoría'}


class DetalleCategoriaProductoView(DetailFormsView):
	model = CategoriaProducto 
	extra_context = {'modelo': 'categoria', 'url_icono': '/img/iconos/48/categoria.png'}
	permission_required = 'productos.change_categoriaproducto'
	add_permission = 'productos.add_categoriaproducto'

	def get_forms(self, context):
		user = self.request.user
		categoria = self.object

		context['form'] = CategoriaProductoForm(instance=categoria)
		context['forms'] = OrderedDict()

		context['forms']['atributos'] = {
			'titulo': 'Atributos',
			'sub_forms': OrderedDict()
		}

		if user.has_perm('productos.add_atributocategoria'):
			context['forms']['atributos']['agregar'] = AgregarAtributoCategoriaForm(categoria)

		can_delete_atributo = user.has_perm('productos.delete_atributocategoria') 
		for atributo in categoria.atributos_actuales:
			if atributo.nombre != categoria.nombre:
				context['forms']['atributos']['sub_forms'][str(atributo)] = {
																	'label': atributo.nombre,
																	'objeto': atributo,
																	}
				if can_delete_atributo:
					context['forms']['atributos']['sub_forms'][str(atributo)]['eliminar'] = EliminarAtributoCategoriaForm(instance=atributo)

	def post(self, request, slug, **kwargs):
		context = super().get_context_data(**kwargs)
		categoria = context['object']

		if CategoriaProductoForm.nombre_form in request.POST:
			form = CategoriaProductoForm(request.POST or None, instance=categoria)

			if categoria.nombre != request.POST['nombre']:
				cambiar_slug = True
			else:
				cambiar_slug = False

			if form.is_valid():
				form.save(cambiar_slug)
				return redirect(categoria)

			context['form'] = form
		elif AgregarAtributoCategoriaForm.nombre_form in request.POST:
			form = AgregarAtributoCategoriaForm(categoria, request.POST or None)
		
			if form.is_valid():
				form.save()
				return redirect(categoria)

			context['forms']['atributos']['agregar'] = form
		elif EliminarAtributoCategoriaForm.nombre_form in request.POST:
			atributo = AtributoCategoria.objects.actuales().get(nombre=request.POST['nombre'], categoria=categoria)
			form = EliminarAtributoCategoriaForm(request.POST or None, instance=atributo)
		
			if form.is_valid():
				form.delete()
				return redirect(categoria)

		return render(request, self.template_name, context)


class DetalleProductoView(DetailFormsView):
	model = Producto
	extra_context = {'modelo': 'producto', 'url_icono': '/img/iconos/48/nuevo-producto.png'}
	permission_required = 'productos.change_producto'
	add_permission = 'productos.add_producto'

	def get_forms(self, context):
		user = self.request.user
		producto = self.object

		context['form'] = ProductoForm(instance=producto)
		context['forms'] = OrderedDict()

		context['forms']['categorias'] = {
			'titulo': 'Categorías',
			'sub_forms': OrderedDict()
		}

		if user.has_perm('productos.add_atributoproducto') and producto.opciones_para_categorias.exists():
			context['forms']['categorias']['agregar'] = AgregarCategoriaProductoForm(producto)

		for categoria in producto.categorias_actuales:
			atributos = OrderedDict()
			for atributo in producto.atributos_actuales_por_categoria(categoria=categoria):
				if atributo.atributo_categoria.nombre != categoria.nombre:
					atributos[str(atributo)] = {
										'titulo': atributo.atributo_categoria.nombre,
										'objeto': atributo,
										}
					if user.has_perm('productos.change_atributoproducto'):
						atributos[str(atributo)]['actualizar'] = ActualizarAtributoProductoForm(instance=atributo)
					else:
						atributos[str(atributo)]['titulo'] += ': '+atributo.valor
			context['forms']['categorias']['sub_forms'][str(categoria)] = {
													'titulo': categoria.nombre,
													'objeto': categoria, 
													'sub_forms': atributos
													}
			if user.has_perm('productos.delete_atributoproducto'):
				context['forms']['categorias']['sub_forms'][str(categoria)]['eliminar'] = EliminarAtributosProductoForm(producto, categoria)

		if producto.producto_pre_fabricado:
			context['forms']['componentes'] = {
				'titulo': 'Componentes',
				'sub_forms': OrderedDict()
			}

			if user.has_perm('productos.add_componenteproducto') and producto.opciones_para_componentes.exists():
				context['forms']['componentes']['agregar'] = AgregarComponenteProductoForm(producto)

			for componente in producto.componentes_producto_actuales:
				context['forms']['componentes']['sub_forms'][str(componente)] = {
														'label': str(componente.producto_componente),
														'objeto': componente.producto_componente,
														}
				if user.has_perm('productos.change_componenteproducto'):
					context['forms']['componentes']['sub_forms'][str(componente)]['actualizar'] = ActualizarComponenteProductoForm(instance=componente)
				else:
					context['forms']['componentes']['sub_forms'][str(componente)]['label'] += ': '+str(componente.cantidad_componente)
				if user.has_perm('productos.delete_componenteproducto'):
					context['forms']['componentes']['sub_forms'][str(componente)]['eliminar'] = EliminarComponenteProductoForm(producto, componente.producto_componente)		
		else:
			context['forms']['proveedores'] = {
				'titulo': 'Proveedores',
				'sub_forms': OrderedDict()
			}

			if user.has_perm('productos.add_proveedorproducto') and producto.opciones_para_proveedores.exists():
				context['forms']['proveedores']['agregar'] = AgregarProveedorProductoForm(producto)

			for proveedor in producto.proveedores_actuales:
				context['forms']['proveedores']['sub_forms'][str(proveedor)] = {
																	'objeto': proveedor
																	}
				if user.has_perm('productos.delete_proveedorproducto'):
					context['forms']['proveedores']['sub_forms'][str(proveedor)]['eliminar'] = EliminarProveedorProductoForm(producto, proveedor)

		context['forms']['stocks'] = {
			'titulo': 'Control de stocks',
			'sub_forms': OrderedDict()
		}

		if user.has_perm('almacenes.add_controlstock') and Almacen.objects.opciones_para_control_stock(producto).exists():
			context['forms']['stocks']['agregar'] = AgregarControlStockForm(producto)

		for control_stock in producto.stocks.actuales():
			context['forms']['stocks']['sub_forms'][str(control_stock)] = {
																'label': str(control_stock.almacen),
																'objeto': control_stock,
																'sub_forms': {}
																}

			if user.has_perm('almacenes.change_controlstock'):
				context['forms']['stocks']['sub_forms'][str(control_stock)]['sub_forms'] = {'actualizar': ActualizarControlStockForm(instance=control_stock)}
			else:
				context['forms']['stocks']['sub_forms'][str(control_stock)]['sub_forms'] = {'actualizar': ActualizarControlStockForm(instance=control_stock, disabled=True)}

	def post(self, request, slug, **kwargs):
		context = super().get_context_data(**kwargs)
		producto = context['object']

		if ProductoForm.nombre_form in request.POST:
			form = ProductoForm(request.POST or None, instance=producto)

			if producto.descripcion != request.POST['descripcion']:
				cambiar_slug = True
			else:
				cambiar_slug = False

			if form.is_valid():
				form.save(cambiar_slug)
				return redirect(producto)

			context['form'] = form

		elif ActualizarAtributoProductoForm.nombre_form in request.POST:
			atributo_producto = producto.atributos_actuales.get(atributo_categoria=request.POST['atributo_categoria'])

			form = ActualizarAtributoProductoForm(request.POST or None, instance=atributo_producto)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['categorias']['sub_forms'][str(atributo_producto.atributo_categoria.categoria)][str(atributo_producto)] = form
		elif ActualizarComponenteProductoForm.nombre_form in request.POST:
			componente_producto = producto.componentes_producto_actuales.get(producto_componente=request.POST['producto_componente'])

			form = ActualizarComponenteProductoForm(request.POST or None, instance=componente_producto)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['componentes']['sub_forms'][str(componente_producto)] = form
		elif ActualizarControlStockForm.nombre_form in request.POST:
			control_stock = ControlStock.objects.get(id=request.POST['control_stock'])

			form = ActualizarControlStockForm(request.POST or None, instance=control_stock)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['stocks']['sub_forms']['actualizar'] = form
		elif AgregarCategoriaProductoForm.nombre_form in request.POST:

			form = AgregarCategoriaProductoForm(producto, request.POST or None)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['categorias']['agregar'] = form
		elif AgregarComponenteProductoForm.nombre_form in request.POST:
			form = AgregarComponenteProductoForm(producto, request.POST or None)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['componentes']['agregar'] = form
		elif AgregarProveedorProductoForm.nombre_form in request.POST:
			form = AgregarProveedorProductoForm(producto, request.POST or None)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['proveedores']['agregar'] = form
		elif AgregarControlStockForm.nombre_form in request.POST:
			form = AgregarControlStockForm(producto, request.POST or None)
		
			if form.is_valid():
				form.save()
				return redirect(producto)

			context['forms']['stocks']['agregar'] = form
		elif EliminarAtributosProductoForm.nombre_form in request.POST:
			categoria = CategoriaProducto.objects.get(id=request.POST['categoria'])
			form = EliminarAtributosProductoForm(producto, categoria, request.POST or None)
		
			if form.is_valid():
				form.delete()
				return redirect(producto)
		elif EliminarComponenteProductoForm.nombre_form in request.POST:
			componente = Producto.objects.get(id=request.POST['producto_componente'])
			form = EliminarComponenteProductoForm(producto, componente, request.POST or None)
		
			if form.is_valid():
				form.delete()
				return redirect(producto)
		elif EliminarProveedorProductoForm.nombre_form in request.POST:
			proveedor = Persona.objects.get(id=request.POST['proveedor'])
			form = EliminarProveedorProductoForm(producto, proveedor, request.POST or None)
		
			if form.is_valid():
				form.delete()
				return redirect(producto)

		return render(request, self.template_name, context)


class ListaProductoView(CreateUpdateListView):
	view_permission = 'productos.view_producto'
	add_permission = 'productos.add_producto'
	change_permission = 'productos.change_producto'
	template_name = 'base_lista.html'
	template_table = 'productos/tabla_body_producto.html'
	paginate_by = 25
	extra_context = {'modelo': 'producto', 'titulo': 'Lista de productos', 'can_add': True}
	delete_form_list = [EliminarProductoForm]
	filter_ = ProductoFilter

	def get_object_forms(self, producto):
	    forms = {}

	    if self.request.user.has_perm('productos.delete_producto') and not UnidadInventario.objects.actuales().filter(control_stock__producto=producto).exists():
		    forms['Eliminar'] = EliminarProductoForm(initial={'object_id':producto.id})
	    return forms


class ListaCategoriaView(CreateUpdateListView):
	view_permission = 'productos.view_categoriaproducto'
	add_permission = 'productos.add_categoriaproducto'
	change_permission = 'productos.change_categoriaproducto'
	template_name = 'base_lista.html'
	template_table = 'productos/tabla_body_categoria.html'
	paginate_by = 25
	extra_context = {'modelo': 'categoria', 'titulo': 'Lista de categorías', 'can_add': True}
	delete_form_list = [EliminarCategoriaProductoForm]
	filter_ = CategoriaProductoFilter

	def get_object_forms(self, categoria_producto):
	    forms = {}
	    
	    if self.request.user.has_perm('productos.delete_categoriaproducto'):
		    if not categoria_producto.productos_actuales.exists():
		    	forms['Eliminar'] = EliminarCategoriaProductoForm(initial={'object_id':categoria_producto.id})
	    return forms


class UnidadesView(CreateUpdateListView):
	view_permission = 'productos.view_unidad'
	add_permission = 'productos.add_unidad'
	change_permission = 'productos.change_unidad'
	extra_context = {'modelo': 'unidad', 'titulo': 'Unidades', 'titulo_form': 'Crear unidad', 'boton_form': 'Crear'}
	form_class = UnidadForm
	updated_message = 'La unidad fue actualizada'
	created_message = 'La unidad fue creada'
	template_table = 'productos/tabla_body_unidad.html'
	paginate_by = 20
	delete_form_list = [EliminarUnidadForm]
	filter_ = UnidadFilter

	def get_object_forms(self, unidad):
	    forms = {}

	    if self.request.user.has_perm('productos.delete_unidad'):
		    if not unidad.productos.filter(activo=True).exists():
		        forms['Eliminar'] = EliminarUnidadForm(initial={'object_id':unidad.id})
	    return forms


    