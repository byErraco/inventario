from rest_framework import serializers 

from .models import Venta, VentaProducto


class VentaSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField()
		
	def create(self, validated_data):
		venta, created = Venta.objects.update_or_create(
	        pk=validated_data.get('id'),
	        defaults={'estado': validated_data.get('estado'), 'activo': validated_data.get('activo')})
		return venta

	class Meta:
		model = Venta
		exclude = ['ultimo_usuario']


class VentaProductoSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField()

	def create(self, validated_data):
		venta_producto, created = VentaProducto.objects.update_or_create(
	        pk=validated_data.get('id'),
	        venta=validated_data.get('venta'),
	        unidad_inventario=validated_data.get('unidad_inventario'),
	        defaults={'cantidad': validated_data.get('cantidad'), 'activo': validated_data.get('activo')})
		return venta_producto

	class Meta:
		model = VentaProducto
		exclude = ['ultimo_usuario']


