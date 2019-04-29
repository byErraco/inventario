from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from personas.models import Persona

from .models import User
from .functions import enviar_email_activacion_usuario


class UserAdminCreateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super(UserAdminCreateForm, self).save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super(UserAdminChangeForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class UsuarioPersonaInlineForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(UsuarioPersonaInlineForm, self).clean()
        
        tipo = cleaned_data.get('tipo')
        numero_identificacion = cleaned_data.get('numero_identificacion')

        if (tipo is not None and self.instance.tipo != tipo) or (numero_identificacion is not None and self.instance.numero_identificacion != numero_identificacion):
            try:
                persona = Persona.objects.actuales().get(tipo=tipo, numero_identificacion=numero_identificacion)
                if persona.usuario is not None:
                    raise forms.ValidationError({'numero_identificacion': _('Existe un usuario con esta identificación.')})
                else:
                    self.instance = persona
            except ObjectDoesNotExist:
                pass

        return cleaned_data

    def save(self, commit=True):
        persona = super(UsuarioPersonaInlineForm, self).save(commit=False)
        enviar_email_activacion_usuario(persona.usuario)
        if commit:
            persona.save()
        return persona

    class Meta:
        model = Persona
        exclude = ('usuario', 'ultimo_usuario', 'fecha_creacion', 'fecha_ultima_modificacion', 'activo',)