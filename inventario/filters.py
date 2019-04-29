from django.db import models

import django_filters 

from almacenes.models import Almacen
from tiendas.models import Tienda


def tiendas_actuales_usuario(request):
    if request is None:
        return Tienda.objects.none()

    return request.user.get_all_tiendas().filter(activo=True)


def almacenes_actuales_tienda_usuario(request, tienda_field='tienda'):
    if request is None:
        return Almacen.objects.none()

    tienda = request.GET.get(tienda_field)
    if tienda:
        return request.user.get_all_almacenes().filter(tienda__id=tienda).actuales()

    return request.user.get_all_almacenes().actuales()


def almacenes_actuales_tienda_usuario_queryset(perm=None, tienda_field='tienda'):
    if perm is None:
        return almacenes_actuales_tienda_usuario

    def almacenes_actuales_tienda_usuario_perm(request):
        if request is None:
            return Almacen.objects.none()

        tienda = request.GET.get(tienda_field)
        if tienda:
            return request.user.get_almacenes_perm(perm).filter(tienda__id=tienda).actuales()

        return request.user.get_almacenes_perm(perm).actuales()

    return almacenes_actuales_tienda_usuario_perm


def tiendas_actuales_usuario_queryset(perm=None):
    if perm is None:
        return tiendas_actuales_usuario

    def tiendas_actuales_usuario_perm(request):
        if request is None:
            return Tienda.objects.none()

        return Tienda.objects.filter(id__in=request.user.get_almacenes_perm(perm).actuales().values_list('tienda', flat=True).distinct()).actuales()

    return tiendas_actuales_usuario_perm


class ActualesFilter(django_filters.FilterSet):

    class Meta:
        abstract = True
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }

    @property
    def qs(self):
        return super().qs.actuales() 


class FechaCreacionFilter(ActualesFilter):
    fecha_creacion_min = django_filters.DateFilter(label='La fecha de creación es mayor o igual a', lookup_expr='date__gte', field_name='fecha_creacion')
    fecha_creacion_max = django_filters.DateFilter(label='La fecha de creación es menor o igual a', lookup_expr='date__lte', field_name='fecha_creacion')