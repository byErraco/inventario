from django.urls import path

from productos.views import DetalleProductoView, CrearProductoView, ListaProductoView, CrearCategoriaProductoView, DetalleCategoriaProductoView, ListaCategoriaView, UnidadesView

app_name = "productos"

urlpatterns = [
	path('', ListaProductoView.as_view(), name ="productos"),
	path('crear/', CrearProductoView.as_view(), name ="crear_producto"),
	path('detalle/<slug:slug>/', DetalleProductoView.as_view(), name ="detalle_producto"),
	path('categorias/', ListaCategoriaView.as_view(), name ="categorias"),
	path('categorias/crear/', CrearCategoriaProductoView.as_view(), name ="crear_categoria"),
	path('categorias/detalle/<slug:slug>/', DetalleCategoriaProductoView.as_view(), name ="detalle_categoria"),
	path('unidades', UnidadesView.as_view(), name ="unidades"),
]