import django_filters

from django.forms import HiddenInput

from inventario.filters import ActualesFilter, FechaCreacionFilter, tiendas_actuales_usuario, almacenes_actuales_tienda_usuario, tiendas_actuales_usuario_queryset, almacenes_actuales_tienda_usuario_queryset

from tiendas.models import Tienda

from .models import Almacen, UnidadInventario, InventarioFisico, UnidadInventarioFisico


class AlmacenFilter(ActualesFilter):
    tienda = django_filters.ModelChoiceFilter(queryset=Tienda.objects.actuales())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['nombre'].label ='El nombre contiene'
        self.filters['direccion'].label ='La dirección contiene'

    class Meta(ActualesFilter.Meta):
        model = Almacen
        fields = ['tienda', 'nombre', 'direccion']   


class UnidadInventarioFilter(ActualesFilter):
    tienda = django_filters.ModelChoiceFilter(label=Tienda._meta.verbose_name.capitalize(), queryset=tiendas_actuales_usuario_queryset('view_unidadinventario'), field_name='control_stock__almacen__tienda')
    almacen = django_filters.ModelChoiceFilter(label=Almacen._meta.verbose_name.capitalize(), queryset=almacenes_actuales_tienda_usuario_queryset('view_unidadinventario'), field_name='control_stock__almacen')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['id'].label ='Id'
        self.filters['control_stock__producto__descripcion'].label ='La descripción contiene'
        self.filters['lote_produccion__codigo'].label ='El código de lote contiene'

    class Meta(ActualesFilter.Meta):
        model = UnidadInventario
        fields = [
            'id', 'tienda', 'almacen', 
            'control_stock__producto__descripcion',
            'lote_produccion__codigo'
        ]

    @property
    def qs(self):
        return super().qs.confirmadas().filter(control_stock__almacen__in=self.request.user.get_all_almacenes().actuales())


class InventarioFisicoFilter(FechaCreacionFilter):
    tienda = django_filters.ModelChoiceFilter(label=Tienda._meta.verbose_name.capitalize(), queryset=tiendas_actuales_usuario_queryset('view_inventariofisico'), field_name='unidades_inventario_fisico__control_stock__almacen__tienda')
    almacen = django_filters.ModelChoiceFilter(label=Almacen._meta.verbose_name.capitalize(), queryset=almacenes_actuales_tienda_usuario_queryset('view_inventariofisico'), field_name='unidades_inventario_fisico__control_stock__almacen')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['usuario_creacion'].label ='Creado por'

    class Meta(ActualesFilter.Meta):
        model = InventarioFisico
        fields = ['tienda', 'almacen', 'usuario_creacion']

    @property
    def qs(self):
        return super().qs.filter(id__in=UnidadInventarioFisico.objects.actuales().filter(unidad_inventario__control_stock__almacen__id__in=self.request.user.get_all_almacenes()).values_list('inventario_fisico', flat=True))   


class UnidadInventarioFisicoFilter(ActualesFilter):

    def __init__(self, data=None, *args, **kwargs):
        inventario_fisico = kwargs.pop('inventario_fisico')

        if data is not None:
            data = data.copy()
            data['inventario_fisico'] = inventario_fisico

        super().__init__(data, *args, **kwargs)

        self.filters['inventario_fisico'].widget = HiddenInput()
        self.filters['unidad_inventario__control_stock__producto'].label ='Producto'
        self.filters['unidad_inventario__lote_produccion__codigo'].label ='Código de lote/serie'

    class Meta(ActualesFilter.Meta):
        model = UnidadInventarioFisico
        fields = ['inventario_fisico', 'unidad_inventario__control_stock__producto', 'unidad_inventario__lote_produccion__codigo']

    @property
    def qs(self):
        return super().qs.con_cantidad_sistema()
