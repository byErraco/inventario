from inventario.filters import ActualesFilter

from .models import Persona


class PersonaFilter(ActualesFilter):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['nombre'].label ='El nombre contiene'
		self.filters['apellido'].label ='El apellido contiene'
		self.filters['tipo'].label ='El tipo de identificación contiene'
		self.filters['numero_identificacion'].label ='El número de identificación contiene'

	class Meta(ActualesFilter.Meta):
		model = Persona
		fields = [ 
            'nombre',
            'apellido',
            'tipo',
            'numero_identificacion'
        ]