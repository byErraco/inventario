from django.test import TestCase

from rest_framework.test import APIRequestFactory

from .views import (
					TiendaAPIView, UnidadesInventarioAPIView, UnidadesInventarioProductosAPIView, 
					UnidadesInventarioAlmacenesAPIView, UnidadesInventarioLotesProduccionAPIView, 
					UnidadesInventarioUnidadesAPIView, VentasAPIView, VentasProductosAPIView
					)


# Create your tests here.

api_key = '7d263dd4882e03ab15faa9a212918ebffd4e97ad'
view = TiendaAPIView.as_view()
factory = APIRequestFactory()
"""
request = factory.get('/api', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Prueba', response.content, '-----------------------\n')


# Obtener las unidades
view = UnidadesInventarioAPIView.as_view()
request = factory.get('/api/unidades_inventario', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Unidades', response.data, '-----------------------\n')


# Obtener los almacenes de las unidades
view = UnidadesInventarioAlmacenesAPIView.as_view()
request = factory.get('/api/unidades_inventario/almacenes', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Almacenes', response.data, '-----------------------\n')


# Obtener los lotes de las unidades
view = UnidadesInventarioLotesProduccionAPIView.as_view()
request = factory.get('/api/unidades_inventario/lotes', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Lotes', response.data, '-----------------------\n')


# Obtener los productos de las unidades
view = UnidadesInventarioProductosAPIView.as_view()
request = factory.get('/api/unidades_inventario/productos', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Productos', response.data, '-----------------------\n')


# Obtener las unidades de los productos
view = UnidadesInventarioUnidadesAPIView.as_view()
request = factory.get('/api/unidades_inventario/unidades', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Unidades de productos', response.data, '-----------------------\n')
"""

# Enviar señal para confirmar que se reciberon las unidades
"""view = UnidadesInventarioAPIView.as_view()
request = factory.post('/api/unidades_inventario', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Confirmación', response.content, '-----------------------\n')"""


# Obtener las unidades otra vez, no se debería recibir nada
"""
request = factory.get('/api/unidades_inventario', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Unidades actualizadas', response.data, '-----------------------\n')"""

# Enviar ventas
view = VentasAPIView.as_view()
request = factory.post('/api/ventas', [{'id': 35, 'estado': 4, 'activo': 1}], format='json', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Respuesta de ventas', response.data, '-----------------------\n')


# Enviar productos en ventas
view = VentasProductosAPIView.as_view()
request = factory.post('/api/ventas/productos', [{'id': 10, 'venta': 1, 'unidad_inventario': 1, 'cantidad': 5}, {'id': 11, 'venta': 1, 'unidad_inventario': 1, 'cantidad': 10}], format='json', HTTP_AUTHORIZATION='api-key {}'.format(api_key))
response = view(request)
print('Respuesta de productos en ventas', response.data, '-----------------------\n')
