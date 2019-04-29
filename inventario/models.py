from django.db import models
from django.db.models import Q

from aenum import UniqueEnum

from inventario.settings import AUTH_USER_MODEL
from inventario.middlewares import RequestMiddleware


class ChoiceEnum(UniqueEnum):
	_init_ = 'value string'

	def __str__(self):
		return self.string

	@classmethod
	def choices(cls):
		return [(choice.value, choice.string.capitalize()) for choice in cls]


class RegistroQuerySet(models.QuerySet):

	def actuales(self):
		return self.filter(activo=True)
		

class RegistroModel(models.Model):
	class Meta:
		abstract = True
		ordering = ['-fecha_ultima_modificacion', '-id']
		
	objects = RegistroQuerySet.as_manager()

	ultimo_usuario = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="registros_%(app_label)s_%(class)s", verbose_name='modificado la última vez por')
	fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')
	fecha_ultima_modificacion = models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')
	activo = models.BooleanField(default=True)

	search_fields = ()
	
	def save(self, *args, **kwargs):
		try: 
			self.ultimo_usuario = RequestMiddleware(get_response=None).thread_local.current_request.user
		except:
			self.ultimo_usuario = None
		super(RegistroModel, self).save(*args, **kwargs)

