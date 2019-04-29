from django import forms
from django.forms.models import BaseInlineFormSet

class DeleteObjectForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['object_id'] = forms.ModelChoiceField(queryset=self.model.objects.all(), widget=forms.HiddenInput())

		initial = kwargs.get('initial')

		if initial:
			self.fields['object_id'].initial = self.model.objects.get(id=initial.get('object_id'))

	def delete(self):
		delete_object = self.cleaned_data['object_id']
		delete_object.activo = False
		delete_object.save()


class RegistroModelForm(forms.ModelForm):
	class Meta:
		fields = ['fecha_creacion', 'fecha_ultima_modificacion', 'ultimo_usuario', 'activo']


class RequiredInlineFormSet(BaseInlineFormSet):

    def _construct_form(self, i, **kwargs):
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form