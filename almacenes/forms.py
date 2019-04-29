from decimal import Decimal

from django import forms
from django.utils.translation import gettext as _

from inventario.forms import DeleteObjectForm
from inventario.middlewares import RequestMiddleware
from productos.models import Producto

from .models import Almacen, UnidadInventario, PrecioUnidadInventario, InventarioFisico, UnidadInventarioFisico, LoteProduccion, ControlStock


class AlmacenForm(forms.ModelForm):
	nombre_form = 'actualizar_almacen'
	titulo_form = 'almacén'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['tienda'].queryset = self.fields['tienda'].queryset.filter(activo=True)

	def save(self, commit=True):
		almacen = super(AlmacenForm, self).save(commit=False)
		if commit:
			almacen.save()
		return almacen

	class Meta:
		model = Almacen
		fields = ['tienda', 'nombre', 'direccion']


class InventarioFisicoForm(forms.ModelForm):
	titulo_form = 'inventario físico'

	almacen = forms.ModelChoiceField(label="Almacén", queryset=Almacen.objects.actuales())

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		user = RequestMiddleware(get_response=None).thread_local.current_request.user

		self.fields['almacen'].queryset = user.get_almacenes_perm('add_inventariofisico').actuales()

	class Meta:
		model = InventarioFisico
		fields = ['almacen']


class UnidadInventarioFisicoBaseFormSet(forms.BaseFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titulo_form = 'productos'

    def clean(self):
    	if not len(self.forms):
    		raise forms.ValidationError('Debe registrar por lo menos un producto')

    	error_minimo = True
    	productos_lotes = {}

    	for form in self.forms:
    		producto = form.cleaned_data.get('producto')
    		
    		if producto:
    			error_minimo = False
	    		if productos_lotes.get(producto.codigo_venta):
	    			if producto.seguimiento:
	    				codigo_lote = form.cleaned_data.get('codigo_lote')

	    				if codigo_lote in productos_lotes[producto.codigo_venta]:
	    					raise forms.ValidationError('Registró varias cantidades para un producto')
	    			else:
	    				raise forms.ValidationError('Registró varias cantidades para un producto')
	    		else:
	    			productos_lotes[producto.codigo_venta] = []

	    			if producto.seguimiento:
	    				codigo_lote = form.cleaned_data.get('codigo_lote')
	    				productos_lotes[producto.codigo_venta].append(codigo_lote)

    	if error_minimo:
    		raise forms.ValidationError('Debe registrar una cantidad de producto como mínimo')


    def save(self, inventario_fisico, almacen):
    	for form in self.forms:
    		form.save(inventario_fisico, almacen)


class UnidadInventarioFisicoForm(forms.Form):
	codigo_venta = forms.CharField(max_length=45, label='Código de venta', required=False)
	codigo_lote = forms.CharField(max_length=255, label='Código de lote', required=False)
	cantidad = forms.DecimalField(max_digits=10, decimal_places=4, min_value=0, required=False)
	
	def clean(self):
		cleaned_data = super().clean()

		codigo_venta = cleaned_data.get('codigo_venta')

		if codigo_venta is not None and codigo_venta != '':
			producto = Producto.objects.actuales().filter(codigo_venta=codigo_venta)
			cantidad = cleaned_data.get('cantidad')

			if len(producto):
				producto = producto[0]

				if not producto.seguimiento and cleaned_data.get('codigo_lote'):
					raise forms.ValidationError({'codigo_lote': 'Este producto no tiene seguimiento'})
				elif producto.seguimiento:
					if not cleaned_data.get('codigo_lote'):
						raise forms.ValidationError({'codigo_lote': 'Este producto tiene seguimiento'})
					if producto.seguimiento == 2:
						if cantidad != 1 and cantidad != 0:
							raise forms.ValidationError({'cantidad': 'La cantidad debe ser 1 o 0'})
				cleaned_data['producto'] = producto
			else:
				raise forms.ValidationError({'codigo_venta': 'No existe un producto con este código de venta'})

			if cantidad is None:
				raise forms.ValidationError({'cantidad': 'Este campo es requerido.'})

		return cleaned_data

	def save(self, inventario_fisico, almacen):
		producto = self.cleaned_data.get('producto')
		codigo_lote = self.cleaned_data.get('codigo_lote')
		cantidad = self.cleaned_data.get('cantidad')

		if producto:
			control_stock = ControlStock.objects.get_or_create(almacen=almacen, producto=producto, activo=True)[0]

			if producto.seguimiento:
				lote_produccion = LoteProduccion.objects.get_or_create(codigo=codigo_lote, producto=producto, activo=True)[0]
			else:
				lote_produccion = None

			unidad_inventario = UnidadInventario.objects.get_or_create(control_stock=control_stock, lote_produccion=lote_produccion, activo=True)[0]

			unidad_inventario_fisico = UnidadInventarioFisico.objects.create(inventario_fisico=inventario_fisico, unidad_inventario=unidad_inventario, cantidad_producto=cantidad)
			return unidad_inventario_fisico

class EliminarAlmacenForm(DeleteObjectForm):
	nombre_form = 'eliminar_almacen'
	model = Almacen


class EliminarInventarioFisicoForm(DeleteObjectForm):
	nombre_form = 'eliminar_inventario_fisico'
	model = InventarioFisico


class PrecioUnidadInventarioForm(forms.ModelForm):
	nombre_form = 'actualizar_precio'
	titulo_form = 'precio'
	
	unidad_inventario = forms.IntegerField(label='Id', min_value=1)
	ganancia = forms.DecimalField(decimal_places=2, min_value=0)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.order_fields(['unidad_inventario', 'base_imponible', 'margen_ganancia', 'ganancia'])
		self.fields['impuesto'].disabled = True
		self.fields['ganancia'].disabled = True
		self.fields['impuesto'].required = False
		self.fields['ganancia'].required = False

	def clean_unidad_inventario(self):
		try:
			return UnidadInventario.objects.get(id=self.cleaned_data['unidad_inventario'])
		except:
			raise forms.ValidationError(_('No se encuentra la unidad de inventario.'))

	def clean(self):
		cleaned_data = super().clean()

		unidad_inventario = cleaned_data.get('unidad_inventario')

		if unidad_inventario is not None:
			user = RequestMiddleware(get_response=None).thread_local.current_request.user
			if not user.has_almacen_perm(unidad_inventario.control_stock.almacen, 'add_preciounidadinventario'):
				raise forms.ValidationError('No tiene permiso para actualizar este elemento.')
		return cleaned_data

	def save(self):
		unidad_inventario = self.cleaned_data['unidad_inventario']
		impuesto = self.data.get('impuesto')
		precio_unidad_inventario = PrecioUnidadInventario.objects.actuales().filter(unidad_inventario=unidad_inventario)
		if len(precio_unidad_inventario):
			precio_unidad_inventario = precio_unidad_inventario[0]
			precio_unidad_inventario.activo = False
			precio_unidad_inventario.save()
		
		precio_unidad_inventario = super(PrecioUnidadInventarioForm, self).save(commit=False)
		precio_unidad_inventario.unidad_inventario = unidad_inventario
		if impuesto:
			precio_unidad_inventario.impuesto = Decimal(impuesto)
		precio_unidad_inventario.save()

		return precio_unidad_inventario

	class Meta:
		model = PrecioUnidadInventario
		fields = ['base_imponible', 'margen_ganancia', 'porcentaje_impuesto', 'impuesto', 'precio_venta_publico', 'exento']


