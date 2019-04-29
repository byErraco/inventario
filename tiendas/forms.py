from django import forms
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext as _

from api.models import TiendaToken

from .models import Tienda


class TiendaForm(forms.ModelForm):

	def save(self, commit=True):
		tienda = super(TiendaForm, self).save(commit=False)
		if commit:
			tienda.save()
		return tienda

	def clean_nombre(self):
		nombre = self.cleaned_data.get('nombre')
		if (nombre is not None and self.instance.nombre != nombre):
			if Tienda.objects.actuales().filter(nombre=nombre).exists():
				raise forms.ValidationError(_('Existe una tienda con este nombre.'))
		return nombre

	class Meta:
		model = Tienda
		fields = ['nombre', 'direccion']


class TiendaTokenInlineForm(forms.ModelForm):
	cambiar_llave = forms.BooleanField(label='Nueva llave', initial=False, required=False)

	def save(self, commit=True):
		if self.cleaned_data.get('cambiar_llave'):
			token = super(TiendaTokenInlineForm, self).save(commit=False)

			if commit:
				token.pk = None
				token.llave = None

				try:
					token_viejo = TiendaToken.objects.get(tienda=self.cleaned_data.get('tienda'), activo=True)
					token_viejo.activo = False
					token_viejo.save()
				except TiendaToken.DoesNotExist:
					pass

				token.save()

			return token
		return None

	class Meta:
		model = TiendaToken
		fields = ['llave']


class TiendaTokenInlineFormSet(BaseInlineFormSet):
    def save_new_objects(self, commit=True):
        saved_instances = super(TiendaTokenInlineFormSet, self).save_new_objects(commit)
        return saved_instances

    def save_existing_objects(self, commit=True):
        saved_instances = super(TiendaTokenInlineFormSet, self).save_existing_objects(commit)
        return saved_instances
