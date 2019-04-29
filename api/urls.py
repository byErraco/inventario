from django.urls import path

from .views import ( 
					TiendaAPIView, UnidadesInventarioAPIView, UnidadesInventarioProductosAPIView, 
					UnidadesInventarioUnidadesAPIView, UnidadesInventarioAlmacenesAPIView, 
					UnidadesInventarioLotesProduccionAPIView, VentasAPIView, VentasProductosAPIView
					)

app_name = "api"

urlpatterns = [
	path('', TiendaAPIView.as_view(), name='tienda'),
	path('ventas', VentasAPIView.as_view(), name='ventas'),
	path('ventas/productos', VentasProductosAPIView.as_view(), name='ventas_productos'),
	path('unidades_inventario', UnidadesInventarioAPIView.as_view(), name='unidades_inventario'),
	path('unidades_inventario/productos', UnidadesInventarioProductosAPIView.as_view(), name='unidades_inventario_productos'),
	path('unidades_inventario/unidades', UnidadesInventarioUnidadesAPIView.as_view(), name='unidades_inventario_unidades'),
	path('unidades_inventario/almacenes', UnidadesInventarioAlmacenesAPIView.as_view(), name='unidades_inventario_almacenes'),
	path('unidades_inventario/lotes', UnidadesInventarioLotesProduccionAPIView.as_view(), name='unidades_inventario_lotes')
]