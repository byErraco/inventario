from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F, Max
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView

from productos.models import Producto, Unidad
from productos.serializers import ProductoSerializer, UnidadSerializer
from almacenes.models import UnidadInventario, Almacen, LoteProduccion, PrecioUnidadInventario
from almacenes.serializers import UnidadInventarioSerializer, AlmacenSerializer, LoteProduccionSerializer
from movimientos.serializers import VentaProductoSerializer, VentaSerializer

from .mixins import CreateListMixin

# Create your views here.


class TiendaAPIView(APIView):
	def get(self, request, format=None):
		return HttpResponse('PRUEBA')

	def post(self, request, format=None):
		return HttpResponse('PRUEBA')


class UnidadesInventarioAPIView(ListAPIView):
	serializer_class = UnidadInventarioSerializer

	def get_queryset(self):
		precios_actualizados = PrecioUnidadInventario.objects.actuales().filter(unidad_inventario__fecha_ultima_sincronizacion__lt=F('fecha_ultima_modificacion'))
		unidades = UnidadInventario.objects.confirmadas().filter(control_stock__almacen__tienda=self.request.user).filter(Q(id__in=precios_actualizados.values_list('unidad_inventario', flat=True)) | Q(fecha_ultima_sincronizacion__isnull=True) | Q(fecha_ultima_sincronizacion__lt=F('fecha_ultima_modificacion'))).annotate(almacen=F('control_stock__almacen__id'), producto=F('control_stock__producto__id'))
		return unidades

	def post(self, request):
		fecha = timezone.now()
		if self.get_queryset().update(fecha_ultima_modificacion=fecha, fecha_ultima_sincronizacion=fecha):
			return JsonResponse({'fecha_ultima_sincronizacion': fecha})
		return JsonResponse('No hay unidades de inventario para sincronizar.', safe=False)


class UnidadesInventarioProductosAPIView(ListAPIView):
	serializer_class = ProductoSerializer

	def get_queryset(self):
		return Producto.objects.raw(
			'SELECT * FROM (SELECT "control_stock"."producto_id", MAX("unidad_inventario"."fecha_ultima_sincronizacion") AS "max_fecha" FROM "unidad_inventario" INNER JOIN "control_stock" ON unidad_inventario.control_stock_id = control_stock.id LEFT JOIN almacen ON control_stock.almacen_id = almacen.id WHERE almacen.tienda_id = %s AND unidad_inventario.id IN %s GROUP BY "control_stock"."producto_id") AS t INNER JOIN producto on producto_id = producto.id WHERE max_fecha IS NULL OR producto.fecha_ultima_modificacion > max_fecha', 
			[self.request.user.id, tuple(UnidadInventario.objects.confirmadas().values_list('id', flat=True))]
		)


class UnidadesInventarioUnidadesAPIView(ListAPIView):
	serializer_class = UnidadSerializer
	
	def get_queryset(self):
		return Unidad.objects.raw(
			'SELECT * FROM (SELECT unidad_id, MAX("unidad_inventario"."fecha_ultima_sincronizacion") AS "max_fecha" FROM unidad_inventario INNER JOIN "control_stock" ON unidad_inventario.control_stock_id = control_stock.id LEFT JOIN almacen ON control_stock.almacen_id = almacen.id LEFT JOIN producto ON producto_id = producto.id INNER JOIN unidad ON producto.unidad_id = unidad.id WHERE almacen.tienda_id = %s AND unidad_inventario.id IN %s GROUP BY unidad_id) AS t INNER JOIN unidad ON unidad_id = unidad.id WHERE max_fecha IS NULL OR unidad.fecha_ultima_modificacion > max_fecha', 
			[self.request.user.id, tuple(UnidadInventario.objects.confirmadas().values_list('id', flat=True))]
		)


class UnidadesInventarioAlmacenesAPIView(ListAPIView):
	serializer_class = AlmacenSerializer
	
	def get_queryset(self):
		return Almacen.objects.raw(
			'SELECT * FROM (SELECT almacen_id, MAX("unidad_inventario"."fecha_ultima_sincronizacion") AS "max_fecha" FROM unidad_inventario INNER JOIN "control_stock" ON unidad_inventario.control_stock_id = control_stock.id LEFT JOIN almacen on control_stock.almacen_id = almacen.id WHERE almacen.tienda_id = %s AND unidad_inventario.id IN %s GROUP BY almacen_id) AS t INNER JOIN almacen ON almacen_id = almacen.id WHERE max_fecha IS NULL OR almacen.fecha_ultima_modificacion > max_fecha', 
			[self.request.user.id, tuple(UnidadInventario.objects.confirmadas().values_list('id', flat=True))]
		)		


class UnidadesInventarioLotesProduccionAPIView(ListAPIView):
	serializer_class = LoteProduccionSerializer
	
	def get_queryset(self):
		return LoteProduccion.objects.raw(
			'SELECT * FROM (SELECT lote_produccion_id, MAX("unidad_inventario"."fecha_ultima_sincronizacion") AS "max_fecha" FROM unidad_inventario INNER JOIN "control_stock" ON unidad_inventario.control_stock_id = control_stock.id LEFT JOIN almacen on control_stock.almacen_id = almacen.id WHERE almacen.tienda_id = %s AND unidad_inventario.id IN %s GROUP BY lote_produccion_id) AS t INNER JOIN lote_produccion ON lote_produccion_id = lote_produccion.id WHERE max_fecha IS NULL OR lote_produccion.fecha_ultima_modificacion > max_fecha', 
			[self.request.user.id, tuple(UnidadInventario.objects.confirmadas().values_list('id', flat=True))]
		)		


class VentasProductosAPIView(CreateListMixin, CreateAPIView):
	serializer_class = VentaProductoSerializer


class VentasAPIView(CreateListMixin, CreateAPIView):
	serializer_class = VentaSerializer