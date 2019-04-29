from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q, F, Sum, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.urls import reverse

from inventario.models import RegistroModel, RegistroQuerySet
from productos.models import Producto
from movimientos.models import TrasladoProducto, CompraProducto, AjusteInventarioProducto, Fabricacion, VentaProducto

# Create your models here.

class AlmacenQuerySet(RegistroQuerySet):
	def actuales(self):
		return self.filter(activo=True).filter(Q(tienda__isnull=True) | Q(tienda__activo=True))

	def opciones_para_control_stock(self, producto):
		return self.exclude(id__in=producto.stocks.actuales().values_list('almacen', flat=True)).actuales()


class Almacen(RegistroModel):
	nombre = models.CharField(max_length=255)
	direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name='dirección')

	tienda = models.ForeignKey('tiendas.Tienda', blank=True, null=True, on_delete=models.CASCADE, related_name='almacenes')

	objects = AlmacenQuerySet.as_manager()
	
	@property
	def productos_actuales(self):
		return Producto.objects.actuales().filter(id__in=self.unidades_inventario_actuales.values_list('control_stock__producto', flat=True)).distinct()

	@property
	def lotes_produccion_inventario_actuales(self):
		return LoteProduccion.objects.actuales().filter(id__in=self.unidades_inventario_actuales.values_list('lote_produccion__id', flat=True)).distinct()

	@property
	def unidades_inventario_actuales(self):
		return UnidadInventario.objects.actuales().confirmadas().filter(control_stock__almacen=self)

	@property
	def traslados_pendientes(self):
		return TrasladoProducto.objects.actuales().sin_confirmar().filter(Q(unidad_inventario_origen__control_stock__almacen=self) | Q(unidad_inventario_destino__control_stock__almacen=self))

	def cantidad_producto(self, producto):
		return self.unidades_inventario_actuales.filter(control_stock__producto=producto).aggregate(cantidad=Coalesce(Sum('cantidad_producto'), 0))['cantidad']

	def opciones_fabricacion(self):
		opciones = {
			'opciones': [],
			'cantidades_produccion_maxima': {}
		}

		for producto in Producto.objects.actuales().pre_fabricados():
			cantidad_produccion_maxima =  producto.cantidad_produccion_maxima(self)
			if cantidad_produccion_maxima:
				opciones['opciones'].append((producto.id, str(producto))) 
				opciones['cantidades_produccion_maxima'][producto.id] = cantidad_produccion_maxima

		return opciones

	def codigos_lotes_producto(self, producto):
		codigos_lotes = self.lotes_produccion_inventario_actuales.filter(producto=producto).values_list('codigo', flat=True)
		codigos_lotes = [(codigo_lote, codigo_lote) for codigo_lote in codigos_lotes]
		return codigos_lotes

	def __str__(self):
		string = ''

		if self.tienda:
			string += str(self.tienda)+'. '

		string += self.nombre

		if self.direccion:
			string += '. '+self.direccion

		return string

	search_fields = ('nombre', 'direccion', 'tienda__nombre')

	class Meta(RegistroModel.Meta):
		db_table = 'almacen'
		verbose_name = 'almacén'
		verbose_name_plural = 'almacenes'
		permissions = (
		        ('view_almacen', 'Can see almacenes'),
		    )


class InventarioFisico(RegistroModel):
	usuario_creacion = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Usuario de creación', null=True, on_delete=models.SET_NULL, related_name='inventarios_fisicos')

	def get_absolute_url(self):
		return reverse("almacenes:detalle_inventario_fisico", kwargs={'id': self.id})

	@property
	def almacen(self):
		return Almacen.objects.get(pk=self.unidades_inventario_fisico.values(almacen=F('unidad_inventario__control_stock__almacen'))[0]['almacen'])
		
	def save(self, *args, **kwargs):
		crear = False
		if self.pk is None: 
			crear = True
		super(InventarioFisico, self).save(*args, **kwargs)
		if crear:
			self.usuario_creacion = self.ultimo_usuario
			self.save()

	class Meta(RegistroModel.Meta):
		db_table = 'inventario_fisico'
		verbose_name = 'inventario físico'
		verbose_name_plural = 'inventarios físicos'
		permissions = (
		        ('view_inventariofisico', 'Can see inventarios físicos'),
		    )


class UnidadInventarioFisicoQuerySet(RegistroQuerySet):

	def con_cantidad_sistema(self):
		ajustes = AjusteInventarioProducto.objects.actuales().filter(unidad_inventario=OuterRef('unidad_inventario')).filter(fecha_creacion__lte=OuterRef('inventario_fisico__fecha_creacion')).order_by().values('unidad_inventario')
		cantidad_ajustes = ajustes.annotate(sum=Sum('cantidad')).values('sum')

		compras = CompraProducto.objects.actuales().filter(unidad_inventario=OuterRef('unidad_inventario')).filter(fecha_creacion__lte=OuterRef('inventario_fisico__fecha_creacion')).order_by().values('unidad_inventario')
		cantidad_compras = compras.annotate(sum=Sum('cantidad')).values('sum')

		traslados_destino = TrasladoProducto.objects.confirmados().filter(unidad_inventario_destino=OuterRef('unidad_inventario')).filter(fecha_creacion__lte=OuterRef('inventario_fisico__fecha_creacion')).order_by().values('unidad_inventario_destino')
		cantidad_traslados_destino = traslados_destino.annotate(sum=Sum('cantidad')).values('sum')

		produccion = Fabricacion.objects.actuales().filter(unidad_inventario=OuterRef('unidad_inventario')).filter(fecha_creacion__lte=OuterRef('inventario_fisico__fecha_creacion')).order_by().values('unidad_inventario')
		cantidad_produccion = produccion.annotate(sum=Sum('cantidad_produccion')).values('sum')

		traslados_origen = TrasladoProducto.objects.actuales().filter(unidad_inventario_origen=OuterRef('unidad_inventario')).filter(fecha_creacion__lte=OuterRef('inventario_fisico__fecha_creacion')).order_by().values('unidad_inventario_origen')
		cantidad_traslados_origen = traslados_origen.annotate(sum=Sum('cantidad')).values('sum')

		ventas = VentaProducto.objects.actuales().filter(unidad_inventario=OuterRef('unidad_inventario')).filter(fecha_creacion__lte=OuterRef('inventario_fisico__fecha_creacion')).order_by().values('unidad_inventario')
		cantidad_ventas = ventas.annotate(sum=Sum('cantidad')).values('sum')
		
		return self.annotate(
			ajustes_sum=Coalesce(Subquery(cantidad_ajustes, models.DecimalField()),0),
			compras_sum=Coalesce(Subquery(cantidad_compras, models.DecimalField()),0),
			traslados_destino_sum=Coalesce(Subquery(cantidad_traslados_destino, models.DecimalField()),0),
			produccion_sum=Coalesce(Subquery(cantidad_produccion, models.DecimalField()),0),
			traslados_origen_sum=Coalesce(Subquery(cantidad_traslados_origen, models.DecimalField()),0),
			ventas_sum=Coalesce(Subquery(cantidad_ventas, models.DecimalField()),0)).annotate(cantidad_sistema=F('ajustes_sum')+F('compras_sum')+F('traslados_destino_sum')+F('produccion_sum')-F('traslados_origen_sum')-F('ventas_sum')).order_by('id')


class UnidadInventarioFisico(RegistroModel):
	inventario_fisico = models.ForeignKey('almacenes.InventarioFisico', on_delete=models.CASCADE, related_name='unidades_inventario_fisico')
	unidad_inventario = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='unidades_inventarios_fisicos')
	cantidad_producto = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'), verbose_name='Cantidad de producto')

	objects = UnidadInventarioFisicoQuerySet.as_manager()
	
	class Meta(RegistroModel.Meta):
		db_table = 'unidad_inventario_fisico'
		verbose_name = 'unidad inventario físico'
		verbose_name_plural = 'unidades inventario físico'


class ControlStockQuerySet(RegistroQuerySet):
	def actuales(self):
		return self.filter(activo=True, almacen__activo=True, producto__activo=True)


class ControlStock(RegistroModel):
	producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='stocks')
	almacen = models.ForeignKey('almacenes.Almacen', on_delete=models.CASCADE, related_name='stocks', verbose_name='almacén')
	stock_minimo = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'), verbose_name='stock mínimo')
	stock_maximo = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=4, verbose_name='stock máximo')

	objects = ControlStockQuerySet.as_manager()

	class Meta(RegistroModel.Meta):
		db_table = 'control_stock'
		verbose_name = 'control de stock'
		verbose_name_plural = 'controles de stock'
		permissions = (
		        ('view_', 'Can see controles de stock'),
		    )


class UnidadInventarioQuerySet(RegistroQuerySet):
	def actuales(self):
		return self.filter(activo=True, control_stock__almacen__activo=True, cantidad_producto__gt=0)

	def confirmadas(self):
		return self.filter(~Q(id__in=TrasladoProducto.objects.actuales().values_list('unidad_inventario_destino', flat=True)) | Q(id__in=TrasladoProducto.objects.actuales().confirmados().values_list('unidad_inventario_destino', flat=True)))


class UnidadInventario(RegistroModel):
	control_stock = models.ForeignKey('almacenes.ControlStock', on_delete=models.CASCADE, related_name='unidades_inventario')
	lote_produccion = models.ForeignKey('almacenes.LoteProduccion', blank=True, null=True, on_delete=models.SET_NULL, related_name='unidades_inventario')
	cantidad_producto = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'), verbose_name='Cantidad de producto')

	objects = UnidadInventarioQuerySet.as_manager()

	fecha_ultima_sincronizacion = models.DateTimeField(null=True, verbose_name='fecha de última sincronización')

	def actualizar_cantidad_producto(self):
	    self.cantidad_producto = self.cantidad_actual()
	    self.save()

	def almacen(self):
		nombre_almacen = self.control_stock.almacen.nombre
		direccion_almacen = self.control_stock.almacen.direccion
		if direccion_almacen is not None:
			nombre_almacen += '. ' + direccion_almacen
		return  nombre_almacen
	almacen.short_description = 'almacén'

	def producto(self):
		return self.control_stock.producto.descripcion

	@property
	def precio_actual(self):
		try:
			return self.precios.get(activo=True)
		except:
			return None

	@property
	def cantidad_actual_sin_ventas(self):
		traslados_sum = self.traslados_destino.confirmados().aggregate(sum=Coalesce(models.Sum('cantidad'), 0))['sum']
		traslados_sum -= self.traslados_origen.actuales().aggregate(sum=Coalesce(models.Sum('cantidad'), 0))['sum']
		compras_sum = self.compras.actuales().aggregate(sum=Coalesce(models.Sum('cantidad'), 0))['sum']
		fabricacion_sum = self.fabricacion.actuales().aggregate(sum=Coalesce(models.Sum('cantidad_produccion'), 0))['sum']
		ajustes_sum = self.ajustes.actuales().aggregate(sum=Coalesce(models.Sum('cantidad'), 0))['sum']

		return traslados_sum+compras_sum+fabricacion_sum+ajustes_sum

	def cantidad_actual(self):
		ventas_sum = -self.ventas.actuales().aggregate(sum=Coalesce(models.Sum('cantidad'), 0))['sum']

		return self.cantidad_actual_sin_ventas+ventas_sum
	cantidad_actual.short_description = 'cantidad actual'

	def codigo_lote(self):
		if self.lote_produccion:
			return self.lote_produccion.codigo
		return 'Ninguno'
	codigo_lote.short_description = 'código de lote/serie'

	search_fields = ('id', 'control_stock_almacen__tienda__nombre', 'control_stock__almacen__nombre', 
					 'control_stock__producto__codigo_venta', 'control_stock__producto__descripcion',
					 'lote_produccion__codigo') 

	class Meta(RegistroModel.Meta):
		db_table = 'unidad_inventario'
		verbose_name = 'unidad de inventario'
		verbose_name_plural = 'unidades de inventario'
		permissions = (
		        ('view_unidadinventario', 'Can see unidades inventario'),
		    )


class PrecioUnidadInventario(RegistroModel):
	unidad_inventario = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='precios')

	base_imponible = models.DecimalField(max_digits=10, decimal_places=2)
	margen_ganancia = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True, verbose_name='margen de ganancia')
	porcentaje_impuesto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='porcentaje de impuesto')
	impuesto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='impuesto')
	precio_venta_publico = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='precio final')
	exento = models.BooleanField(default=False)

	objects = RegistroQuerySet.as_manager()
	
	def almacen(self):
		return self.unidad_inventario.almacen()
	almacen.short_description = 'almacén'

	def producto(self):
		return self.unidad_inventario.producto()

	def codigo_lote(self):
		if self.unidad_inventario.lote_produccion:
			return self.unidad_inventario.lote_produccion.codigo
		return 'Ninguno'
	codigo_lote.short_description = 'código de lote/serie'

	def __str__(self):
		return str(self.precio_venta_publico)+'_'+str(self.unidad_inventario)

	search_fields = ('unidad_inventario__control_stock__almacen__tienda__nombre', 'unidad_inventario__control_stock__almacen__nombre', 'unidad_inventario__control_stock__almacen__direccion', 'unidad_inventario__control_stock__producto__codigo_venta', 'unidad_inventario__control_stock__producto__descripcion', 'unidad_inventario__lote_produccion__codigo')

	class Meta(RegistroModel.Meta):
		db_table = 'precio_unidad_inventario'
		verbose_name = 'precio'
		verbose_name_plural = 'precios'


class LoteProduccion(RegistroModel):
	codigo = models.CharField(max_length=255)
	producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='lotes_produccion')
	fecha_produccion = models.DateField(null=True)
	fecha_vencimiento = models.DateField(null=True)

	objects = RegistroQuerySet.as_manager()

	def __str__(self):
		return self.codigo

	class Meta(RegistroModel.Meta):
		db_table = 'lote_produccion'
		permissions = (
		        ('view_loteproduccion', 'Can see lotes produccion'),
		    )