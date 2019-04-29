from rest_framework import serializers

from .models import Unidad, Producto


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        exclude = ['ultimo_usuario']


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        exclude = ['ultimo_usuario']

