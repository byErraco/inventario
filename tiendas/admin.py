from django.contrib import admin

from inventario.admin import RegistroAdmin
from api.models import TiendaToken

from .models import Tienda
from .forms import TiendaForm, TiendaTokenInlineForm, TiendaTokenInlineFormSet

# Register your models here.


class TokenInline(admin.StackedInline):
    model = TiendaToken
    fk_name = 'tienda'
    can_delete = False
    form = TiendaTokenInlineForm
    formset = TiendaTokenInlineFormSet
    extra = 1
    max_num = 1
    readonly_fields = ('llave',)

    def get_queryset(self, request):
    	qs = super().get_queryset(request)
    	return qs.filter(activo=True)


@admin.register(Tienda)
class TiendaAdmin(RegistroAdmin):
	form = TiendaForm
	add_form = form

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs, permissions=True)

	def change_view(self, request, object_id, form_url='', extra_context=None):
	    self.inlines = [TokenInline]
	    return super().change_view(request, object_id)

	def add_view(self, request, form_url='', extra_context=None):
		self.inlines = []
		return super().add_view(request)

	fieldsets = (
	    (None, { 'fields': ('nombre', 'direccion')}),
	)

	list_display = ('nombre', 'direccion')