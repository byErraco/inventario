from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator

from inventario.models import RegistroModel, RegistroQuerySet

# Create your models here.


class Persona(RegistroModel):
	usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='persona', blank=True, null=True)
	nombre = models.CharField(max_length=45)
	apellido = models.CharField(max_length=45, blank=True, null=True)
	tipo = models.CharField(max_length=1, verbose_name='tipo de identificación')
	numero_identificacion = models.CharField(max_length=45, verbose_name='número de identificación')
	direccion = models.CharField(max_length=100, blank=True, null=True, verbose_name='dirección')
	telefono = models.CharField(max_length=45, blank=True, null=True, verbose_name='teléfono')
	email = models.EmailField(verbose_name='dirección de correo electrónico', blank=True, null=True)
	twitter = models.CharField(max_length=15, blank=True, null=True, validators=[RegexValidator(r'^[0-9a-zA-Z_]*$', "Solo se permiten caracteres alfanuméricos y '_'.")])
	instagram = models.CharField(max_length=30, blank=True, null=True, validators=[RegexValidator(r'^[0-9a-zA-Z_\.]*$', "Solo se permiten caracteres alfanuméricos, '.' y '_'.")])
	facebook = models.CharField(max_length=50, blank=True, null=True, validators=[MinLengthValidator(5), RegexValidator(r'^[0-9a-zA-Z\.]*$', "Solo se permiten caracteres alfanuméricos y '.'.")])
	representante = models.ForeignKey('personas.Persona', on_delete=models.SET_NULL, blank=True, null=True)
	
	objects = RegistroQuerySet.as_manager()
	
	def identificacion(self):
		return self.tipo+'-'+self.numero_identificacion
	identificacion.short_description = 'identificación'

	def __str__(self):
		string = self.nombre

		if self.apellido:
			string += ' '+self.apellido

		return string+'. '+self.tipo+'-'+self.numero_identificacion

	search_fields = ('nombre', 'apellido', 'tipo', 'numero_identificacion')
	
	class Meta(RegistroModel.Meta):
		db_table = 'persona'
		permissions = (
		        ('view_persona', 'Can see personas'),
		    )