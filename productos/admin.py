from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from inventario.admin import RegistroAdmin

from .models import Producto, CategoriaProducto, Unidad

# Register your models here.

class FabricadoListFilter(admin.SimpleListFilter):
    title = _('fabricado')
    parameter_name = 'fabricado'

    def lookups(self, request, model_admin):
        return (
            ('si', _('Si')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.no_fabricados()
        if self.value() == 'si':
            return queryset.fabricados()


@admin.register(Producto)
class ProductoAdmin(RegistroAdmin):

	fieldsets = (
	    (None, { 'fields': ('codigo_venta', 'descripcion', 'unidad', 'balanza', 
				  'producto_pre_fabricado',
				  'seguimiento')}),
	)

	list_display = (
		'codigo_venta', 'descripcion', 'unidad', 'balanza', 'fabricado_property', 'producto_pre_fabricado', 
		'seguimiento')
	list_filter = ('unidad', FabricadoListFilter, 'producto_pre_fabricado', 'seguimiento')

	search_fields = ('codigo_venta', 'descripcion')


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(RegistroAdmin):

	fieldsets = (
	    (None, { 'fields': ('nombre',)}),
	)

	list_display = ('nombre',)
	search_fields = ('nombre',)


@admin.register(Unidad)
class UnidadAdmin(RegistroAdmin):

	fieldsets = (
	    (None, { 'fields': ('nombre', 'descripcion')}),
	)

	list_display = ('nombre', 'descripcion')
	search_fields = ('nombre', 'descripcion')
