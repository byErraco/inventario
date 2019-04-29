from django.db.models import Sum
from django.db.models.functions import Coalesce

import django_filters

from inventario.filters import ActualesFilter, almacenes_actuales_tienda_usuario_queryset, tiendas_actuales_usuario_queryset

from tiendas.models import Tienda
from almacenes.models import Almacen

from .models import Producto, CategoriaProducto, Unidad


class ProductoFilter(ActualesFilter):

    def tienda_filter(self, queryset, name, value):
        if value and not len(self.data.get('almacen')):
            return queryset.filter(stocks__almacen__tienda=value)
        return queryset

    def categoria_filter(self, queryset, name, value):
        categorias = self.data.getlist('categorias[]')

        if len(categorias):
            if 'null' in categorias:
                if len(categorias) == 1:
                    return queryset.exclude(atributos__activo=True)
                return queryset.none()

            queryset = queryset.filter(id__in=CategoriaProducto.objects.get(id=int(categorias[0])).productos_actuales.values_list('id', flat=True))

            for categoria in categorias[1:]:
                queryset = queryset.filter(id__in=CategoriaProducto.objects.get(id=int(categoria)).productos_actuales.values_list('id', flat=True))

        return queryset

    tienda = django_filters.ModelChoiceFilter(label=Tienda._meta.verbose_name.capitalize(), queryset=tiendas_actuales_usuario_queryset('view_unidadinventario'), method='tienda_filter')
    almacen = django_filters.ModelChoiceFilter(label=Almacen._meta.verbose_name.capitalize(), field_name='stocks__almacen', queryset=almacenes_actuales_tienda_usuario_queryset('view_unidadinventario'))
    unidad = django_filters.ModelChoiceFilter(field_name='unidad', queryset=Unidad.objects.actuales(), null_label='Unidad')
    seguimiento = django_filters.ChoiceFilter(field_name='seguimiento', choices=Producto.Seguimiento.choices(), null_label='Ninguno')
    categorias = django_filters.ModelMultipleChoiceFilter(label=CategoriaProducto._meta.verbose_name_plural.capitalize(), null_label='Ninguna', method='categoria_filter', queryset=CategoriaProducto.objects.actuales())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['codigo_venta'].label = 'El código de venta contiene'
        self.filters['descripcion'].label = 'La descripción contiene'
       
    @property
    def qs(self):
        qs = super().qs.annotate(cantidad_disponible=Coalesce(Sum('stocks__unidades_inventario__cantidad_producto'), 0))
        return qs

    class Meta(ActualesFilter.Meta):
        model = Producto
        fields = [
            'codigo_venta',
            'descripcion',
            'unidad',
            'balanza',
            'producto_pre_fabricado',
            'seguimiento',
            'categorias',
            'tienda',
            'almacen'
        ]


class CategoriaProductoFilter(ActualesFilter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['nombre'].label ='El nombre contiene'

    class Meta(ActualesFilter.Meta):
        model = CategoriaProducto
        fields = [
            'nombre',
        ]


class UnidadFilter(ActualesFilter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['nombre'].label ='El nombre contiene'
        self.filters['descripcion'].label ='La descripción contiene'

    class Meta(ActualesFilter.Meta):
        model = Unidad
        fields = [
            'nombre',
            'descripcion'
        ]