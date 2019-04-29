from django.contrib import admin

from inventario.admin import RegistroAdmin

from .models import Persona
from .forms import PersonaForm

# Register your models here.


@admin.register(Persona)
class PersonaAdmin(RegistroAdmin):
	form = PersonaForm
	add_form = form

	fieldsets = (
	    (None, { 'fields': ('usuario', 'nombre', 'apellido', ('tipo', 'numero_identificacion'), 
				  'direccion', 'telefono')}),
	)

	list_display = ('usuario', 'nombre', 'apellido', 'identificacion')

	search_fields = ('usuario__email', 'nombre', 'apellido', 'identificacion')

	readonly_fields = ('usuario',)