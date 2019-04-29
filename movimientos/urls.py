from django.urls import path

from .views import (VentasProductoView, ComprasProductoView, CompraProductoCreateUpdateView, CompraProductoFormView, 
					TrasladosProductoView, TrasladoProductoCreateUpdateView, TrasladoProductoFormView, 
					AjustesInventarioProductoView, AjusteInventarioProductoCreateView, AjusteInventarioProductoFormView, 
					FabricacionView, FabricacionCreateView, FabricacionFormView, 
					ComprasReportView, AjustesReportView, VentasReportView, 
					FabricacionReportView, TrasladosReportView)


app_name = "movimientos"

urlpatterns = [
	path('ventas/', VentasProductoView.as_view(), name ="ventas"),
	path('ventas/reporte', VentasReportView.as_view(), name="reporte_venta"),
	path('compras/', ComprasProductoView.as_view(), name ="compras"),
	path('compras/reporte', ComprasReportView.as_view(), name="reporte_compra"),
	path('compras/form/procesar', CompraProductoCreateUpdateView.as_view(), name ="compra_form_procesar"),
	path('compras/form/obtener', CompraProductoFormView.as_view(), name ="compra_form_obtener"),
	path('traslados/', TrasladosProductoView.as_view(), name ="traslados"),
	path('traslados/reporte', TrasladosReportView.as_view(), name="reporte_traslado"),
	path('traslados/form/procesar', TrasladoProductoCreateUpdateView.as_view(), name ="traslado_form_procesar"),
	path('traslados/form/obtener', TrasladoProductoFormView.as_view(), name ="traslado_form_obtener"),
	path('ajustes/', AjustesInventarioProductoView.as_view(), name ="ajustes"),
	path('ajustes/reporte', AjustesReportView.as_view(), name="reporte_ajuste"),
	path('ajustes/form/procesar', AjusteInventarioProductoCreateView.as_view(), name ="ajuste_form_procesar"),
	path('ajustes/form/obtener', AjusteInventarioProductoFormView.as_view(), name ="ajuste_form_obtener"),
	path('fabricacion/', FabricacionView.as_view(), name ="fabricacion"),
	path('fabricacion/reporte', FabricacionReportView.as_view(), name="reporte_fabricacion"),
	path('fabricacion/form/procesar', FabricacionCreateView.as_view(), name ="fabricacion_form_procesar"),
	path('fabricacion/form/obtener', FabricacionFormView.as_view(), name ="fabricacion_form_obtener")
]