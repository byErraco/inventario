from django.urls import resolve, reverse_lazy


def app(request):
    return {'app': resolve(request.path).app_name}

def menu(request):
	user = request.user

	try:
		if user.is_authenticated:
			urls = []
			urlsAlmacenes = []
			urlsMovimientos = []
			urlsProductos = []
			
			if user.has_perm('tiendas.view_tienda'):
				urls.append({'url': reverse_lazy('tiendas:tiendas'), 'text':'Tiendas'})

			if user.has_model_perms('almacenes', 'almacen'):
				urlsAlmacenes.append({'url': reverse_lazy('almacenes:almacenes'), 'text':'Almacenes'})
			if user.has_model_perms('almacenes', 'unidadinventario') or user.has_model_perms('almacenes', 'preciounidadinventario'):
				urlsAlmacenes.append({'url': reverse_lazy('almacenes:unidades'), 'text':'Productos'})
			if user.has_model_perms('almacenes', 'inventariofisico'):
				urlsAlmacenes.append({'url': reverse_lazy('almacenes:inventarios_fisicos'), 'text':'Inventario físico'})

			urls.append({'urls': urlsAlmacenes, 'text':'Inventario'})

			if user.has_model_perms('movimientos', 'ventaproducto'):
				urlsMovimientos.append({'url': reverse_lazy('movimientos:ventas'), 'text':'Ventas'})
			if user.has_model_perms('movimientos', 'compraproducto'):
				urlsMovimientos.append({'url': reverse_lazy('movimientos:compras'), 'text':'Compras'})
			if user.has_model_perms('movimientos', 'trasladoproducto'):
				urlsMovimientos.append({'url': reverse_lazy('movimientos:traslados'), 'text':'Traslados'})
			if user.has_model_perms('movimientos', 'ajusteinventarioproducto'):
				urlsMovimientos.append({'url': reverse_lazy('movimientos:ajustes'), 'text':'Ajustes'})
			if user.has_model_perms('movimientos', 'fabricacion'):
				urlsMovimientos.append({'url': reverse_lazy('movimientos:fabricacion'), 'text':'Fabricación'})

			urls.append({'urls': urlsMovimientos, 'text':'Movimientos'})

			if user.has_model_perms('productos', 'producto'):
				urlsProductos.append({'url': reverse_lazy('productos:productos'), 'text':'Productos'})
			if user.has_model_perms('productos', 'categoriaproducto'):
				urlsProductos.append({'url': reverse_lazy('productos:categorias'), 'text':'Categorías'})
			if user.has_model_perms('productos', 'unidad'):
				urlsProductos.append({'url': reverse_lazy('productos:unidades'), 'text':'Unidades'})

			urls.append({'urls': urlsProductos, 'text':'Productos'})

			if user.has_module_perms('personas'):
				urls.append({'url': reverse_lazy('personas:personas'), 'text':'Personas'})

			for item in urls:
				if 'url' in item:
					if item['url'] == request.path:
						item['active'] = 'active'
				else:
					for sub_item in item['urls']:
						if sub_item['url'] == request.path:
							sub_item['active'] = 'active'
							item['active'] = 'active'
			
			if user.is_staff:
				urls.append({'urls': [{'url': reverse_lazy('admin:index'), 'text':'Administrador'}], 'text':'Configuración'})

			return {'urls': urls}
	except AttributeError:
		return {}
	return {}