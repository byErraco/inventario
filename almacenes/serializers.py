from rest_framework import serializers 

from .models import Almacen, PrecioUnidadInventario, UnidadInventario, LoteProduccion


class AlmacenSerializer(serializers.ModelSerializer):
	class Meta:
		model = Almacen
		exclude = ['tienda', 'ultimo_usuario']


class LoteProduccionSerializer(serializers.ModelSerializer):
	class Meta:
		model = LoteProduccion
		exclude = ['ultimo_usuario']


class PrecioUnidadInventarioSerializer(serializers.ModelSerializer):
	class Meta:
		model = PrecioUnidadInventario
		exclude = ['unidad_inventario', 'ultimo_usuario']


class UnidadInventarioSerializer(serializers.ModelSerializer):
	
	precio_actual = PrecioUnidadInventarioSerializer()
	cantidad_actual_sin_ventas = serializers.DecimalField(max_digits=10, decimal_places=4)
	almacen = serializers.IntegerField()
	producto = serializers.IntegerField()

	def get_precio_actual(self, obj):
		return obj.precio_actual

	def get_cantidad_actual_sin_ventas(self, obj):
	    return obj.cantidad_actual_sin_ventas

	class Meta:
		model = UnidadInventario
		exclude = ['fecha_ultima_sincronizacion', 'ultimo_usuario', 'control_stock']