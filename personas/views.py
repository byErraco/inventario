from inventario.views import CreateUpdateListView

from .models import Persona
from .forms import PersonaForm, EliminarPersonaForm
from .filters import PersonaFilter

# Create your views here.

class PersonasView(CreateUpdateListView):
    view_permission = 'personas.view_persona'
    add_permission = 'personas.add_persona'
    change_permission = 'personas.change_persona'
    updated_message = "La persona fue actualizada"
    created_message = "La persona fue creada"
    form_class = PersonaForm
    extra_context = {'modelo': 'persona', 'titulo': 'Personas', 'titulo_form': 'Crear/Actualizar persona', 'boton_form': 'Actualizar'}
    template_table = 'personas/tabla_body_persona.html'
    paginate_by = 20
    delete_form_list = [EliminarPersonaForm]
    filter_ = PersonaFilter

    def get_object_forms(self, persona):
        forms = {}
        
        if self.request.user.has_perm('personas.delete_persona'):
            if persona.usuario is None and not persona.productos_proveedor.filter(activo=True, producto__activo=True).exists():
                forms['Eliminar'] = EliminarPersonaForm(initial={'object_id':persona.id})

        return forms
    
    def get_object(self, request):
        try:
            return Persona.objects.actuales().get(tipo=request.POST['tipo'], numero_identificacion=request.POST['numero_identificacion'])
        except:
            return None
