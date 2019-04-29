from django.db import models

from inventario.models import RegistroModel, RegistroQuerySet
# Create your models here.


class Tienda(RegistroModel):
	nombre = models.CharField(max_length=255)
	direccion = models.CharField(max_length=255, verbose_name='dirección')

	objects = RegistroQuerySet.as_manager()

	search_fields = ('nombre', 'direccion')
		
	def is_authenticated(self):
		return True
		
	def __str__(self):
		if Tienda.objects.actuales().filter(nombre=self.nombre).count() > 1:
			return '{} {}'.format(self.id, self.nombre)
		return self.nombre

	class Meta(RegistroModel.Meta):
		db_table = 'tienda'
		permissions = (
		        ('view_tienda', 'Can see tiendas'),
		    )
