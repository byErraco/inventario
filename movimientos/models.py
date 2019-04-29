from django.db import models

from inventario.models import ChoiceEnum, RegistroModel, RegistroQuerySet

# Create your models here.


class AjusteInventarioProducto(RegistroModel):
	unidad_inventario = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='ajustes')
	cantidad = models.DecimalField(max_digits=10, decimal_places=4)
	descripcion = models.CharField(max_length=100, blank=True, null=True)

	objects = RegistroQuerySet.as_manager()

	def save(self, *args, **kwargs):
	    super(AjusteInventarioProducto, self).save(*args, **kwargs)
	    self.unidad_inventario.actualizar_cantidad_producto()

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

	fabricacion = models.ForeignKey('movimientos.Fabricacion', null=True, on_delete=models.CASCADE, related_name='ajustes')

	search_fields = ('unidad_inventario__control_stock__almacen__nombre', 'unidad_inventario__control_stock__producto__descripcion',
					 'unidad_inventario__lote_produccion__codigo')
	
	class Meta(RegistroModel.Meta):
		db_table = 'ajuste_inventario_producto'
		verbose_name = 'ajuste'
		verbose_name_plural = 'ajustes'
		permissions = (
		        ('view_ajusteinventarioproducto', 'Can see ajustes inventario producto'),
		    )


class TrasladoProductoQuerySet(RegistroQuerySet):
	def sin_confirmar(self):
		return self.actuales().filter(fecha_confirmacion__isnull=True)

	def confirmados(self):
		return self.actuales().filter(fecha_confirmacion__isnull=False)


class TrasladoProducto(RegistroModel):
	unidad_inventario_origen = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='traslados_origen')
	unidad_inventario_destino = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='traslados_destino')

	cantidad = models.DecimalField(max_digits=10, decimal_places=4)
	costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	fecha_confirmacion = models.DateTimeField(null=True)

	objects = TrasladoProductoQuerySet.as_manager()

	def save(self, *args, **kwargs):
	    super(TrasladoProducto, self).save(*args, **kwargs)
	    self.unidad_inventario_origen.actualizar_cantidad_producto()
	    self.unidad_inventario_destino.actualizar_cantidad_producto()

	def almacen_origen(self):
		return self.unidad_inventario_origen.almacen()
	almacen_origen.short_description = 'almacén origen'

	def almacen_destino(self):
		return self.unidad_inventario_destino.almacen()
	almacen_destino.short_description = 'almacén destino'

	def producto(self):
		return self.unidad_inventario_origen.producto()

	def codigo_lote(self):
		if self.unidad_inventario_origen.lote_produccion:
			return self.unidad_inventario_origen.lote_produccion.codigo
		return 'Ninguno'
	codigo_lote.short_description = 'código de lote/serie'

	search_fields = ('unidad_inventario_origen__control_stock__almacen__nombre', 'unidad_inventario_origen__control_stock__producto__codigo_venta', 
					 'unidad_inventario_origen__control_stock__producto__descripcion', 'unidad_inventario_origen__lote_produccion__codigo',
					 'unidad_inventario_destino__control_stock__almacen__nombre')

	class Meta(RegistroModel.Meta):
		db_table = 'traslado_producto'
		verbose_name = 'traslado'
		verbose_name_plural = 'traslados'
		permissions = (
		        ('view_trasladoproducto', 'Can see traslados producto'),
		        ('confirm_trasladoproducto', 'Can confirm traslado producto'),
		    )


class Venta(RegistroModel):
	class Estado(ChoiceEnum):
		EN_PROCESO = 1, 'en proceso'
		FINALIZADA = 2, 'finalizada'
		PAUSADA = 3, 'pausada'
		CANCELADA = 4, 'cancelada'

	estado = models.IntegerField(choices=Estado.choices()); 

	objects = RegistroQuerySet.as_manager()

	def estado_str(self):
		return str(self.Estado(self.estado))

	class Meta(RegistroModel.Meta):
		db_table = 'venta'


class VentaProducto(RegistroModel):

	class VentaProductoQuerySet(RegistroQuerySet):
		def actuales(self):
			return self.filter(activo=True, venta__activo=True).exclude(venta__estado=Venta.Estado.CANCELADA.value)

	venta = models.ForeignKey('movimientos.Venta', on_delete=models.CASCADE, related_name='venta_productos'); 
	unidad_inventario = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='ventas')

	cantidad = models.DecimalField(max_digits=10, decimal_places=4)

	objects = VentaProductoQuerySet.as_manager()

	def save(self, *args, **kwargs):
	    super(VentaProducto, self).save(*args, **kwargs)
	    self.unidad_inventario.actualizar_cantidad_producto()

	search_fields = ('unidad_inventario__control_stock__producto__descripcion', 'unidad_inventario__control_stock__producto__codigo_venta', 
					 'unidad_inventario__control_stock__almacen__tienda__nombre', 'unidad_inventario__control_stock__almacen__tienda__direccion',
					 'unidad_inventario__control_stock__almacen__nombre', 'unidad_inventario__control_stock__almacen__direccion', 
					 'unidad_inventario__lote_produccion__codigo')

	class Meta(RegistroModel.Meta):
		db_table = 'venta_producto'
		verbose_name = 'venta'
		verbose_name_plural = 'ventas'
		permissions = (
		        ('view_ventaproducto', 'Can see ventas producto'),
		    )


class CompraProducto(RegistroModel):
	unidad_inventario = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='compras')
	proveedor = models.ForeignKey('personas.Persona', on_delete=models.CASCADE, related_name='compras_proveedor')

	cantidad = models.DecimalField(max_digits=10, decimal_places=4)
	costo_unidad = models.DecimalField(max_digits=10, decimal_places=2)

	objects = RegistroQuerySet.as_manager()

	def save(self, *args, **kwargs):
	    super(CompraProducto, self).save(*args, **kwargs)
	    self.unidad_inventario.actualizar_cantidad_producto()

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

	@property
	def costo_adicional(self):
		return self.costos.filter(activo=True).aggregate(models.Sum('cantidad'))['cantidad__sum']

	search_fields = ('unidad_inventario__control_stock__producto__descripcion', 'unidad_inventario__control_stock__producto__codigo_venta', 
					 'proveedor__nombre', 'proveedor__apellido', 'proveedor__numero_identificacion', 
					 'unidad_inventario__control_stock__almacen__nombre', 'unidad_inventario__control_stock__almacen__direccion', 
					 'unidad_inventario__lote_produccion__codigo')

	class Meta(RegistroModel.Meta):
		db_table = 'compra_producto'
		verbose_name = 'compra'
		verbose_name_plural = 'compras'
		permissions = (
		        ('view_compraproducto', 'Can see compras producto'),
		    )


class CostoCompra(RegistroModel):
	compra_producto = models.ForeignKey('movimientos.CompraProducto', on_delete=models.CASCADE, related_name='costos')

	descripcion = models.CharField(max_length=40, verbose_name='Descripción')
	cantidad = models.DecimalField(max_digits=10, decimal_places=2)
		
	class Meta(RegistroModel.Meta):
		db_table = 'costo_compra'
		verbose_name = 'costo adicional'
		verbose_name_plural = 'costos adicionales'


class Fabricacion(RegistroModel):
	lote_produccion = models.OneToOneField('almacenes.LoteProduccion', on_delete=models.CASCADE, related_name='fabricacion')
	unidad_inventario = models.ForeignKey('almacenes.UnidadInventario', on_delete=models.CASCADE, related_name='fabricacion')
	cantidad_produccion = models.DecimalField(null=True, max_digits=10, decimal_places=4, verbose_name='cantidad')

	objects = RegistroQuerySet.as_manager()

	def save(self, *args, **kwargs):
	   	super(Fabricacion, self).save(*args, **kwargs)
	   	self.unidad_inventario.actualizar_cantidad_producto()

	def producto(self):
		return self.lote_produccion.producto.descripcion

	def almacen_produccion(self):
		return self.unidad_inventario.almacen()
	almacen_produccion.short_description = 'almacén'
	
	def codigo_lote(self):
		return self.lote_produccion.codigo
	codigo_lote.short_description = 'código de lote/serie'

	def fecha_produccion(self):
		return self.lote_produccion.fecha_produccion
	fecha_produccion.short_description = 'fecha de producción'

	def fecha_vencimiento(self):
		return self.lote_produccion.fecha_vencimiento
	fecha_vencimiento.short_description = 'fecha de vencimiento'

	search_fields = ('unidad_inventario__control_stock__almacen__nombre', 'unidad_inventario__control_stock__almacen__direccion',
					 'lote_produccion__producto__codigo_venta', 'lote_produccion__producto__descripcion',
					 'lote_produccion__codigo')
	
	class Meta(RegistroModel.Meta):
		db_table = 'fabricacion'
		verbose_name = 'fabricación'
		permissions = (
		        ('view_fabricacion', 'Can see fabricacion'),
		    )
