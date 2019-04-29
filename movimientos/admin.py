from django.contrib import admin

from inventario.admin import RegistroAdmin
from almacenes.models import LoteProduccion

from .models import CompraProducto, TrasladoProducto, AjusteInventarioProducto, Fabricacion

# Register your models here.


@admin.register(CompraProducto)
class CompraProductoAdmin(RegistroAdmin):
	list_display = ('almacen', 'producto', 'codigo_lote', 'proveedor', 'cantidad', 'costo_unidad', 'costos_adicionales_display')
	list_display_links = None
	list_filter = ('proveedor',)

	def costos_adicionales_display(self, obj):
		costos = ''
		for costo in obj.costos.all():
			costos += costo.descripcion+': '+str(costo.cantidad)+'\n'
		return costos
	costos_adicionales_display.short_description = 'costos adicionales'

	def has_add_permission(self, request):
	    return False


@admin.register(TrasladoProducto)
class TrasladoProductoAdmin(RegistroAdmin):
	list_display = ('almacen_origen', 'producto', 'codigo_lote', 'cantidad', 'costo', 'almacen_destino', 'fecha_confirmacion')
	list_display_links = None

	def has_add_permission(self, request):
	    return False


@admin.register(AjusteInventarioProducto)
class AjusteInventarioProductoAdmin(RegistroAdmin):
	list_display = ('almacen', 'producto', 'codigo_lote', 'cantidad', 'descripcion')
	list_display_links = None

	def has_add_permission(self, request):
	    return False


@admin.register(Fabricacion)
class FabricacionProductoAdmin(RegistroAdmin):
	list_display = ('codigo_lote', 'almacen_produccion', 'producto', 'cantidad_produccion', 'fecha_produccion', 'fecha_vencimiento')
	list_display_links = None
	
	def has_add_permission(self, request):
	    return False
