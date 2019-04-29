from django import forms
from django.utils.translation import gettext as _

from inventario.forms import DeleteObjectForm

from .models import Persona


class PersonaForm(forms.ModelForm):
	nombre_form = 'actualizar_persona'
	titulo_form = 'persona'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		if self.instance.pk is not None:
			self.fields['representante'].queryset =Persona.objects.actuales().exclude(pk=self.instance.pk)

	def save(self, commit=True):
		persona = super(PersonaForm, self).save(commit=False)
		if commit:
			persona.save()
		return persona

	def clean(self):
		cleaned_data = super(PersonaForm, self).clean()
		
		tipo = cleaned_data.get('tipo')
		numero_identificacion = cleaned_data.get('numero_identificacion')

		if (tipo is not None and self.instance.tipo != tipo) or (numero_identificacion is not None and self.instance.numero_identificacion != numero_identificacion):
			if Persona.objects.actuales().filter(tipo=tipo, numero_identificacion=numero_identificacion).exists():
				raise forms.ValidationError({'numero_identificacion': _('Existe una persona con esta identificación.')})

		return cleaned_data

	class Meta:
		model = Persona
		fields = ['nombre', 'apellido', 'tipo', 'numero_identificacion', 
				  'direccion', 'telefono', 'email', 'twitter', 'facebook', 'instagram', 'representante']


class EliminarPersonaForm(DeleteObjectForm):
	nombre_form = 'eliminar_persona'
	model = Persona