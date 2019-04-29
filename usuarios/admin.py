from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import ugettext_lazy as _

from inventario.forms import RequiredInlineFormSet
from personas.models import Persona

from .forms import UserAdminCreateForm, UserAdminChangeForm, UsuarioPersonaInlineForm
from .models import User
from .functions import enviar_email_activacion_usuario


class PersonaInline(admin.StackedInline):
    model = Persona
    fk_name = 'usuario'
    can_delete = False
    verbose_name_plural = 'personas'
    form = UsuarioPersonaInlineForm
    formset = RequiredInlineFormSet

    def get_readonly_fields(self, request, obj=None):
    	try:
    		obj
    		obj.persona 
    		return ['tipo', 'numero_identificacion']
    	except:
    		return []


@admin.register(User)
class UserAdmin(UserAdmin):
	form = UserAdminChangeForm
	add_form = UserAdminCreateForm

	inlines = (PersonaInline,)

	fieldsets = (
        (None, {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions', 'user_almacenes')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
	add_fieldsets = (
	    (None, {
	        'classes': ('wide',),
	        'fields': ('email',),
	    }),
	)
	filter_horizontal = ['groups', 'user_permissions', 'user_almacenes']
	list_display = ('email', 'is_active', 'is_staff')
	search_fields = ('email',)
	ordering = ('email',)

	def get_readonly_fields(self, request, obj=None):
		if obj:
			return ('email',)
		return ()

	def enviar_emails_activacion_usuarios(self, request, queryset):
		num_users = len(queryset)
		
		queryset = queryset.filter(is_active=False)
		num_users_no_active = len(queryset)
		num_enviados = 0

		for user in queryset:
			num_enviados += enviar_email_activacion_usuario(user)

		if num_users_no_active != num_users:
			self.message_user(request, 'Solo se envian correos de activación a los usuarios inactivos.', level=messages.WARNING)

		if num_enviados != num_users_no_active:
			self.message_user(request, 'Se enviaron correos de activación a %i de %i usuarios.' % (num_enviados, num_users_no_active), level=messages.WARNING)
		else:
		    if num_enviados == 1:
		       	self.message_user(request, 'Se envió un correo de activación.')
		    else:
		    	self.message_user(request, 'Se enviaron %s correos de activación.' % num_enviados)

	enviar_emails_activacion_usuarios.short_description = 'Enviar correo para activación de usuario'

	actions = [enviar_emails_activacion_usuarios, ]

admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(GroupAdmin):
	filter_horizontal = ('permissions', 'almacenes')
