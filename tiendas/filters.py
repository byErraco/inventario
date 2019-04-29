from inventario.filters import ActualesFilter

from .models import Tienda


class TiendaFilter(ActualesFilter):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.filters['nombre'].label ='El nombre contiene'
		self.filters['direccion'].label ='La dirección contiene'

	class Meta(ActualesFilter.Meta):
		model = Tienda
		fields = [
			'nombre',
			'direccion'
		]
