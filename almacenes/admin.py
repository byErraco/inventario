from django.contrib import admin

from inventario.admin import RegistroAdmin

from .models import Almacen, UnidadInventario, PrecioUnidadInventario
from .forms import AlmacenForm

# Register your models here.


@admin.register(Almacen)
class AlmacenAdmin(RegistroAdmin):

	fieldsets = (
	    (None, { 'fields': ('tienda', 'nombre', 'direccion')}),
	)

	list_display = ('tienda', 'nombre', 'direccion')

	search_fields = ('tienda__nombre', 'nombre', 'direccion')

	change_readonly_fields = ('tienda',)


@admin.register(UnidadInventario)
class UnidadInventarioAdmin(RegistroAdmin):
	list_display = ('almacen', 'producto', 'codigo_lote', 'cantidad_producto', 'precio_display')
	
	def precio_display(self, obj):
		precio_actual = obj.precio_actual

		if precio_actual is not None:
			precio = 'Precio: {}, Base imponible: {}, Ganancia %: {}, Impuesto %: {}, Exento: {}'.format(
					precio_actual.precio_venta_publico if precio_actual.precio_venta_publico else '-', precio_actual.base_imponible if precio_actual.base_imponible else '-', precio_actual.margen_ganancia if precio_actual.margen_ganancia else '-', 
					precio_actual.porcentaje_impuesto if precio_actual.porcentaje_impuesto else '-', 'Si' if precio_actual.exento else 'No' 
				)
		else:
			precio = 'Precio: -, Base imponible: -, Ganancia %: -, Impuesto %: -, Exento: -'
		return precio
	precio_display.short_description = 'precio actual'


@admin.register(PrecioUnidadInventario)
class PrecioUnidadInventarioAdmin(RegistroAdmin):
	list_display = ('almacen', 'producto', 'codigo_lote', 'precio_venta_publico', 'base_imponible', 'margen_ganancia', 'porcentaje_impuesto', 'impuesto', 'exento')

