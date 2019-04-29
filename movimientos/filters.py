import django_filters

from inventario.filters import FechaCreacionFilter, tiendas_actuales_usuario_queryset, almacenes_actuales_tienda_usuario_queryset

from tiendas.models import Tienda
from almacenes.models import Almacen

from .models import VentaProducto, CompraProducto, AjusteInventarioProducto, Fabricacion, TrasladoProducto



class MovimientoFilter(FechaCreacionFilter):
	permission = None

	tienda = django_filters.ModelChoiceFilter(label=Tienda._meta.verbose_name.capitalize(), queryset=Tienda.objects.actuales(), field_name='unidad_inventario__control_stock__almacen__tienda')
	almacen = django_filters.ModelChoiceFilter(label=Almacen._meta.verbose_name.capitalize(), queryset=Almacen.objects.actuales(), field_name='unidad_inventario__control_stock__almacen')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['unidad_inventario__control_stock__producto__descripcion'].label ='La descripción del producto contiene'
		self.filters['unidad_inventario__control_stock__producto__descripcion'].lookup_expr='icontains'
		self.filters['unidad_inventario__lote_produccion__codigo'].label = 'Código de lote'

		self.filters['tienda'].queryset = tiendas_actuales_usuario_queryset(self.permission)
		self.filters['almacen'].queryset = almacenes_actuales_tienda_usuario_queryset(self.permission)

	class Meta:
		abstract = True


class AjusteInventarioProductoFilter(MovimientoFilter):
	permission = 'view_ajusteinventarioproducto'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['descripcion'].label ='La descripción del ajuste contiene'
		self.filters['descripcion'].lookup_expr='icontains'

	class Meta:
		model = AjusteInventarioProducto
		fields = [
        	'tienda',
        	'almacen',
        	'unidad_inventario__control_stock__producto__descripcion',
        	'unidad_inventario__lote_produccion__codigo',
        	'descripcion'
        ]


class VentaProductoFilter(MovimientoFilter):
	permission = 'view_ventaproducto'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['venta__id'].label = 'Id de venta'
		self.filters['venta__estado'].label = 'Estado de venta'

	class Meta:
		model = VentaProducto
		fields = [
        	'tienda',
        	'almacen',
        	'unidad_inventario__control_stock__producto__descripcion',
        	'unidad_inventario__lote_produccion__codigo',
        	'venta__id',
        	'venta__estado'
        ]


class CompraProductoFilter(MovimientoFilter):
	permission = 'view_compraproducto'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['proveedor__tipo'].label ='Tipo de proveedor'
		self.filters['proveedor__numero_identificacion'].label ='Número de identificación del proveedor'

	class Meta:
		model = CompraProducto
		fields = [
        	'tienda',
        	'almacen',
        	'unidad_inventario__control_stock__producto__descripcion',
        	'unidad_inventario__lote_produccion__codigo',
        	'proveedor__tipo',
        	'proveedor__numero_identificacion'
        ]


class FabricacionFilter(MovimientoFilter):
	permission = 'view_fabricacion'

	class Meta:
		model = Fabricacion
		fields = [
        	'tienda',
        	'almacen',
        	'unidad_inventario__control_stock__producto__descripcion',
        	'unidad_inventario__lote_produccion__codigo'
        ]


class TrasladoProductoFilter(FechaCreacionFilter):

	tienda_origen = django_filters.ModelChoiceFilter(label='Tienda de origen', queryset=tiendas_actuales_usuario_queryset('view_trasladoproducto'), field_name='unidad_inventario_origen__control_stock__almacen__tienda')
	almacen_origen = django_filters.ModelChoiceFilter(label='Almacén de origen', queryset=almacenes_actuales_tienda_usuario_queryset('view_trasladoproducto', tienda_field='tienda_origen'), field_name='unidad_inventario_origen__control_stock__almacen')

	tienda_destino = django_filters.ModelChoiceFilter(label='Tienda destino', queryset=tiendas_actuales_usuario_queryset('view_trasladoproducto'), field_name='unidad_inventario_destino__control_stock__almacen__tienda')
	almacen_destino = django_filters.ModelChoiceFilter(label='Almacén destino', queryset=almacenes_actuales_tienda_usuario_queryset('view_trasladoproducto', tienda_field='tienda_destino'), field_name='unidad_inventario_destino__control_stock__almacen')

	confirmados = django_filters.BooleanFilter(label='Traslado confirmado', field_name='fecha_confirmacion', lookup_expr='isnull', exclude=True)


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['unidad_inventario_origen__control_stock__producto__descripcion'].label ='La descripción del producto contiene'
		self.filters['unidad_inventario_origen__control_stock__producto__descripcion'].lookup_expr='icontains'
		self.filters['unidad_inventario_origen__lote_produccion__codigo'].label = 'Código de lote'

	class Meta:
		model = TrasladoProducto
		fields = [
        	'tienda_origen',
        	'almacen_origen',
        	'unidad_inventario_origen__control_stock__producto__descripcion',
        	'unidad_inventario_origen__lote_produccion__codigo',
        	'tienda_destino',
        	'almacen_destino'
        ]