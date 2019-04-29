from django.urls import path
from .views import AlmacenesView, UnidadesInventarioView, InventariosFisicosView, CrearInventarioFisicoView, InventarioFisicoFormView, DetalleInventarioFisicoView, InventarioFisicoReportView

app_name = "almacenes"

urlpatterns = [
	path('', AlmacenesView.as_view(), name ="almacenes"),
	path('unidades', UnidadesInventarioView.as_view(), name ="unidades"),
	path('inventarios_fisicos/', InventariosFisicosView.as_view(), name ="inventarios_fisicos"),
	path('inventarios_fisicos/crear/', CrearInventarioFisicoView.as_view(), name ="crear_inventario_fisico"),
	path('inventarios_fisicos/crear/form/obtener', InventarioFisicoFormView.as_view(), name ="inventario_fisico_form_obtener"),
	path('inventarios_fisicos/detalle/<int:id>/', DetalleInventarioFisicoView.as_view(), name ="detalle_inventario_fisico"),
	path('inventarios_fisicos/reporte/<int:id>/', InventarioFisicoReportView.as_view(), name="reporte_inventario_fisico"),
]