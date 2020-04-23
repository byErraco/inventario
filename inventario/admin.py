from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


def deactivate_objects(modeladmin, request, queryset):
	for obj in queryset:
		obj.activo = False
		obj.save()
deactivate_objects.short_description = 'Desactivar elementos seleccionados'

def has_add_permission(request):
    return False

class RegistroAdmin(admin.ModelAdmin):

	readonly_fields = ()
	change_readonly_fields = ()
	list_display = ()
	list_filter = ()
	actions = []
	search_fields = ()

	def __init__(self, *args, **kwargs):
		permissions = kwargs.pop('permissions', None)

		super().__init__(*args, **kwargs)
		self.readonly_fields += ('fecha_creacion', 'fecha_ultima_modificacion', 'ultimo_usuario', 'activo')
		self.list_display = ('id',) + self.list_display + ('fecha_creacion', 'fecha_ultima_modificacion', 'ultimo_usuario', 'activo')
		self.list_filter = ('activo',) + self.list_filter
		self.actions += [deactivate_objects]
		self.search_fields += ('id',)

		if not permissions:
			self.has_add_permission = has_add_permission
			list_display_links = None

	def get_fieldsets(self, request, obj=None):
		if obj:
			return self.fieldsets + ((_('Important dates'), { 'fields': ('fecha_creacion', 'fecha_ultima_modificacion', 'ultimo_usuario', 'activo')}),)
		return self.fieldsets

	def get_readonly_fields(self, request, obj=None):
		if obj:
			if not obj.activo:
				fields = ()
				for fieldset in self.get_fieldsets(request, obj):
					fields += fieldset[1]['fields']
				return fields
			return set(self.change_readonly_fields + self.readonly_fields)
		return self.readonly_fields

	class Meta:
		abstract = True
