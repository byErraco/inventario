import re
from decimal import getcontext, Decimal

from django import forms
from django.utils.translation import gettext as _
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum

from inventario.middlewares import RequestMiddleware
from inventario.forms import DeleteObjectForm
from almacenes.models import Almacen, UnidadInventario, LoteProduccion, ControlStock
from productos.models import Producto, CategoriaProducto
from personas.models import Persona

from .models import CompraProducto, CostoCompra, TrasladoProducto, AjusteInventarioProducto, Fabricacion


def MayorQueCeroValidator(valor):
    if valor <= 0:
        raise ValidationError(_('Asegúrese de que este valor es mayor que 0.'))


def MenorQueCeroValidator(valor):
    if valor >= 0:
        raise ValidationError(_('Asegúrese de que este valor es menor que 0.'))


class ModelNullChoiceIterator(forms.models.ModelChoiceIterator):
	def __iter__(self):
		if self.field.empty_label is not None:
		    yield ('', self.field.empty_label)

		if self.field.null_label is not None:
			yield('null', self.field.null_label)

		queryset = self.queryset

		if not queryset._prefetch_related_lookups:
		    queryset = queryset.iterator()
		for obj in queryset:
		    yield self.choice(obj)


class ModelMultipleNullChoiceField(forms.ModelMultipleChoiceField):

	iterator = ModelNullChoiceIterator

	def __init__(self, *args, **kwargs):
		self.null_label = kwargs.pop('null_label')
		super().__init__(*args, **kwargs)
	   

class EliminarCompraProductoForm(DeleteObjectForm):
	nombre_form = 'eliminar_compra_producto'
	model = CompraProducto


class CompraProductoForm(forms.ModelForm):
	nombre_form = 'crear_compra'
	titulo_form = 'compra'

	almacen = forms.ModelChoiceField(label="Almacén", queryset=Almacen.objects.actuales())
	categorias = ModelMultipleNullChoiceField(label="Categorías", required=False, null_label='Ninguna', queryset=CategoriaProducto.objects.actuales())
	producto = forms.ModelChoiceField(label="Producto", queryset=Producto.objects.actuales().filter(producto_pre_fabricado=False))

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		initials = kwargs.get('initial')

		if initials:
			almacen_id = initials.get('almacen')
			categorias_ids = initials.get('categorias[]')
			proveedor_id = initials.get('proveedor')
			codigo_lote = initials.get('codigo_lote')
			cantidad = initials.get('cantidad')
			fecha_produccion = initials.get('fecha_produccion')
			fecha_vencimiento = initials.get('fecha_vencimiento')

			changed_data = initials.get('changed_data')

			if changed_data == 'categorias':
				producto_id = None
			else:
				producto_id = initials.get('producto')
		else:
			almacen_id = self.data.get('almacen')
			categorias_ids = self.data.get('categorias[]')
			producto_id = self.data.get('producto')
			proveedor_id = self.data.get('proveedor')
			codigo_lote = self.data.get('codigo_lote')
			cantidad = self.data.get('cantidad')
			fecha_produccion = self.data.get('fecha_produccion')
			fecha_vencimiento = self.data.get('fecha_vencimiento')

		user = RequestMiddleware(get_response=None).thread_local.current_request.user

		self.fields['almacen'].queryset = user.get_almacenes_perm('add_compraproducto').actuales()

		if almacen_id:
			self.fields['almacen'].initial = Almacen.objects.get(id=almacen_id)

		if categorias_ids:
			if 'null' in categorias_ids:
				if categorias_ids == 'null':
					self.fields['producto'].queryset = Producto.objects.actuales().exclude(atributos_categoria__activo=True)
				else:
					self.fields['producto'].queryset = Producto.objects.none()
			else:
				if isinstance(categorias_ids, list):
					producto_queryset = Producto.objects.actuales().intersection(CategoriaProducto.objects.get(id=int(categorias_ids[0])).productos_actuales)
					
					for categoria_id in categorias_ids[1:]:
						producto_queryset = producto_queryset.intersection(CategoriaProducto.objects.get(id=int(categoria_id)).productos_actuales)
						
					self.fields['producto'].queryset = producto_queryset
				else:
					producto_queryset = Producto.objects.actuales().intersection(CategoriaProducto.objects.get(id=int(categorias_ids)).productos_actuales)

		if producto_id:
			producto = Producto.objects.get(id=producto_id)
			self.fields['producto'].initial = producto

			self.fields['proveedor'] = forms.ModelChoiceField(label="Proveedor", queryset=Producto.objects.get(id=producto_id).proveedores_actuales)

			if proveedor_id:
				self.fields['proveedor'].initial = Persona.objects.get(id=proveedor_id)

			self.fields['cantidad'] = forms.DecimalField(max_digits=10, decimal_places=4)
			self.fields['cantidad'].validators.append(MayorQueCeroValidator)

			if producto.seguimiento:
				self.fields['codigo_lote'] = forms.CharField(label='Código de lote/serie', max_length=255)

				if producto.seguimiento == 2:
					self.fields['cantidad'].required = False
					self.fields['cantidad'].widget = forms.HiddenInput()
				else:
					self.fields['cantidad'].initial = cantidad
					if producto.seguimiento == 1 and codigo_lote:
						try:
							LoteProduccion.objects.actuales().get(producto=producto, codigo=codigo_lote)
						except:						
							self.fields['fecha_produccion'] = forms.DateField(label="Fecha de producción", required=False)
							self.fields['fecha_vencimiento'] = forms.DateField(label="Fecha de vencimiento", required=False)

							self.fields['fecha_produccion'].initial = fecha_produccion
							self.fields['fecha_vencimiento'].initial = fecha_vencimiento

		self.order_fields(['almacen', 'categorias', 'producto', 'cantidad', 'codigo_lote', 'fecha_produccion', 'fecha_vencimiento', 'proveedor', 'costo_unidad'])

	def clean_categorias(self):
		pass

	def clean(self):
		cleaned_data = super().clean()

		producto = cleaned_data['producto']

		if producto.seguimiento == 2:
			cleaned_data['cantidad'] = 1
			try:
				UnidadInventario.objects.filter(activo=True).get(control_stock__producto=producto, lote_produccion__codigo=cleaned_data['codigo_lote'])
				serie_existe = True
			except:
				serie_existe = False
			if serie_existe:
				raise forms.ValidationError({'codigo_lote': _('Existe un producto en inventario con este número de serie.')})

		almacen = cleaned_data['almacen']
		control_stock = ControlStock.objects.filter(activo=True, producto=producto, almacen=almacen)
		
		if control_stock.exists():
			control_stock = control_stock[0]

			if control_stock.stock_maximo is not None:
				diferencia = cleaned_data['cantidad'] + almacen.cantidad_producto(producto) - control_stock.stock_maximo
				if diferencia > 0:
					raise forms.ValidationError({'cantidad': 'La cantidad total del producto en el almacén supera su stock máximo por '+str(diferencia)})
		return cleaned_data

	def save(self):
		almacen = self.cleaned_data.get('almacen')
		producto = self.cleaned_data.get('producto')
		codigo_lote = self.cleaned_data.get('codigo_lote')
		control_stock = ControlStock.objects.get_or_create(almacen=almacen, producto=producto)[0]
		cantidad = self.cleaned_data.get('cantidad')
		if not cantidad or producto.seguimiento == 2:
			cantidad = 1

		if not producto.seguimiento:
			unidad_inventario, creado = UnidadInventario.objects.get_or_create(control_stock=control_stock, lote_produccion=None, activo=True)
		else:
			lote_produccion, creado = LoteProduccion.objects.actuales().get_or_create(codigo=codigo_lote, producto=producto, activo=True, defaults={'fecha_produccion': self.cleaned_data.get('fecha_produccion'), 'fecha_vencimiento': self.cleaned_data.get('fecha_vencimiento')})

			unidad_inventario, creado = UnidadInventario.objects.get_or_create(control_stock=control_stock, lote_produccion=lote_produccion, activo=True, defaults={'cantidad_producto':cantidad})

		compra_producto = super(CompraProductoForm, self).save(commit=False)
		compra_producto.unidad_inventario = unidad_inventario
		compra_producto.proveedor = self.cleaned_data['proveedor']
		compra_producto.cantidad = cantidad
		compra_producto.save()

		return compra_producto
		
	class Meta:
		model = CompraProducto
		fields = ['costo_unidad']
		labels = {
			'costo_unidad': ('Costo por unidad'),
		}


class CostoCompraForm(forms.ModelForm):
	
	class Meta:
		model = CostoCompra
		fields = ['descripcion', 'cantidad']
		labels = {
			'descripcion': ('Descripción')
		}


CostoCompraFormset = forms.inlineformset_factory(CompraProducto, CostoCompra,
                                            form=CostoCompraForm, extra=1, can_delete=False)
CostoCompraFormset.titulo_form = 'costos'


class ConfirmarTrasladoProductoForm(forms.Form):
	nombre_form = 'confirmar_traslado_producto'
	
	object_id = forms.ModelChoiceField(queryset=TrasladoProducto.objects.all(), widget=forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		initial = kwargs.get('object_id')

		if initial:
			self.fields['object_id'].initial = TrasladoProducto.objects.get(id=initial.get('object_id'))

	def save(self):
		traslado_producto = self.cleaned_data['object_id']
		traslado_producto.fecha_confirmacion = timezone.now()
		traslado_producto.save()


class EliminarTrasladoProductoForm(DeleteObjectForm):
	nombre_form = 'eliminar_traslado_producto'
	model = TrasladoProducto


class TrasladoProductoForm(forms.ModelForm):
	titulo_form = 'traslado'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		initials = kwargs.get('initial')

		if initials:
			almacen_origen_id = initials.get('almacen_origen')
			categorias_ids = initials.get('categorias[]')

			changed_data = initials.get('changed_data')

			if not changed_data:
				producto_id = initials.get('producto')
				codigo_lote = initials.get('codigo_lote')
			elif changed_data != 'almacen_origen' and changed_data != 'categorias':
				producto_id = initials.get('producto')

				if changed_data != 'producto':
					codigo_lote = initials.get('codigo_lote')
				else:
					codigo_lote = None
			else:
				producto_id = None
				codigo_lote = None
		else:
			almacen_origen_id = self.data.get('almacen_origen')
			categorias_ids = self.data.get('categorias[]')
			producto_id = self.data.get('producto')
			codigo_lote = self.data.get('codigo_lote')

		user = RequestMiddleware(get_response=None).thread_local.current_request.user
		self.fields['almacen_origen'] = forms.ModelChoiceField(label="Almacén de origen", queryset=user.get_almacenes_perm('add_trasladoproducto').actuales())

		if almacen_origen_id:
			almacen = Almacen.objects.get(id=almacen_origen_id)

			opciones = almacen.productos_actuales

			if len(opciones):

				self.fields['categorias'] = ModelMultipleNullChoiceField(label="Categorías", required=False, null_label='Ninguna', queryset=CategoriaProducto.objects.actuales())
				
				if categorias_ids:
					if 'null' in categorias_ids:
						if categorias_ids == 'null':
							opciones = opciones.exclude(atributos_categoria__activo=True)
						else:
							opciones = Producto.objects.none()
					else:
						if isinstance(categorias_ids, list):
							for categoria_id in categorias_ids:
								opciones = opciones.intersection(CategoriaProducto.objects.get(id=categoria_id).productos_actuales)
						else:
							opciones = opciones.intersection(CategoriaProducto.objects.get(id=categorias_ids).productos_actuales)

				if producto_id:
					producto = Producto.objects.get(id=producto_id)
				else:
					if len(opciones):
						producto = Producto.objects.get(id=opciones[0].id)
					else:
						producto = None

				if producto is not None:
					self.fields['producto'] = forms.ModelChoiceField(label="Producto", queryset=opciones, empty_label=None)
					self.fields['producto'].initial = producto

					cantidad_field = self.fields['cantidad'] = forms.DecimalField(max_digits=10, decimal_places=4)

					if producto.seguimiento:
						opciones = almacen.codigos_lotes_producto(producto)
						self.fields['codigo_lote'] = forms.ChoiceField(label='Código de lote/serie', choices=opciones)

						if codigo_lote:
							self.fields['codigo_lote'].initial = codigo_lote
							cantidad_query = Q(control_stock__producto=producto, lote_produccion__codigo=codigo_lote)
						else:
							cantidad_query = Q(control_stock__producto=producto, lote_produccion__codigo=opciones[0][0])

						if producto.seguimiento == 2:
							cantidad_field.required = False
							cantidad_field.widget = forms.HiddenInput()
					else:
						cantidad_query = Q(control_stock__producto=producto)
					
					cantidad_max_value = almacen.unidades_inventario_actuales.get(cantidad_query).cantidad_producto

					cantidad_field.validators.append(MaxValueValidator(cantidad_max_value))
					cantidad_field.validators.append(MayorQueCeroValidator)

					cantidad_field.label = "Cantidad ("+str(cantidad_max_value)+" máximo)"

					self.fields['almacen_destino'] = forms.ModelChoiceField(label="Almacén destino", queryset=Almacen.objects.actuales().exclude(id=almacen_origen_id))
				else:
					self.fields['producto'] = forms.ModelChoiceField(label="Producto", queryset=opciones)

		self.order_fields(['almacen_origen', 'categorias', 'producto', 'codigo_lote', 'cantidad', 'costo', 'almacen_destino'])

	def clean_categorias(self):
		pass

	def clean(self):
		cleaned_data = super().clean()

		producto = cleaned_data['producto']
		almacen = cleaned_data['almacen_destino']
		control_stock = ControlStock.objects.filter(activo=True, producto=producto, almacen=almacen)
		
		if producto.seguimiento == 2:
			cleaned_data['cantidad'] = 1

		if control_stock.exists():
			control_stock = control_stock[0]

			if control_stock.stock_maximo is not None:
				diferencia = cleaned_data['cantidad'] + almacen.cantidad_producto(producto) - control_stock.stock_maximo
				if diferencia > 0:
					raise forms.ValidationError({'cantidad_produccion': 'La cantidad total del producto en el almacén de destino supera su stock máximo por '+str(diferencia)})


	def save(self):
		cantidad = self.cleaned_data.get('cantidad')
		if not cantidad:
			cantidad = 1

		almacen_origen = self.cleaned_data['almacen_origen']
		almacen_destino = self.cleaned_data['almacen_destino']
		producto = self.cleaned_data['producto']

		if producto.seguimiento:
			codigo_lote = self.cleaned_data.get('codigo_lote')
			lote_produccion = LoteProduccion.objects.actuales().get(codigo=codigo_lote, producto=producto)
			
			unidad_inventario_origen = almacen_origen.unidades_inventario_actuales.get(control_stock__producto=producto, lote_produccion=lote_produccion)
		else:
			lote_produccion = None
			unidad_inventario_origen = almacen_origen.unidades_inventario_actuales.get(control_stock__producto=producto)

		control_stock = ControlStock.objects.get_or_create(almacen=almacen_destino, producto=producto)[0]
		unidad_inventario_destino, creado = UnidadInventario.objects.get_or_create(control_stock=control_stock, lote_produccion=lote_produccion, activo=True)

		traslado_producto = super().save(commit=False)
		traslado_producto.unidad_inventario_origen = unidad_inventario_origen
		traslado_producto.unidad_inventario_destino = unidad_inventario_destino
		traslado_producto.cantidad = cantidad
		traslado_producto.save()

		return traslado_producto

	class Meta:
		model = TrasladoProducto
		fields = ['costo']


class EliminarAjusteInventarioProductoForm(DeleteObjectForm):
	nombre_form = 'eliminar_ajuste_inventario_producto'
	model = AjusteInventarioProducto


class AjusteInventarioProductoForm(forms.ModelForm):
	titulo_form = 'ajuste'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		initials = kwargs.get('initial')

		if initials:
			almacen_id = initials.get('almacen')
			categorias_ids = initials.get('categorias[]')

			changed_data = initials.get('changed_data')

			if not changed_data:
				producto_id = initials.get('producto')
				codigo_lote = initials.get('codigo_lote')
			elif changed_data != 'almacen' and changed_data != 'categorias':
				producto_id = initials.get('producto')

				if changed_data != 'producto':
					codigo_lote = initials.get('codigo_lote')
				else:
					codigo_lote = None
			else:
				producto_id = None
				codigo_lote = None

		else:
			almacen_id = self.data.get('almacen')
			categorias_ids = self.data.get('categorias[]')
			producto_id = self.data.get('producto')
			codigo_lote = self.data.get('codigo_lote')

		user = RequestMiddleware(get_response=None).thread_local.current_request.user
		self.fields['almacen'] = forms.ModelChoiceField(label="Almacén", queryset=user.get_almacenes_perm('add_ajusteinventarioproducto').actuales())

		if almacen_id:
			almacen = Almacen.objects.get(id=almacen_id)

			opciones = almacen.productos_actuales

			self.fields['categorias'] = ModelMultipleNullChoiceField(label="Categorías", required=False, null_label='Ninguna', queryset=CategoriaProducto.objects.actuales())
	
			if categorias_ids:
				if 'null' in categorias_ids:
					if categorias_ids == 'null':
						opciones = opciones.exclude(atributos_categoria__activo=True)
					else:
						opciones = Producto.objects.none()
				else:
					if isinstance(categorias_ids, list):
						for categoria_id in categorias_ids:
							opciones = opciones.intersection(CategoriaProducto.objects.get(id=categoria_id).productos_actuales)
					else:
						opciones = opciones.intersection(CategoriaProducto.objects.get(id=categorias_ids).productos_actuales)

			if producto_id:
				producto = Producto.objects.get(id=producto_id)
			else:
				if len(opciones):
					producto = Producto.objects.get(id=opciones[0].id)
				else:
					producto = None

			if producto is not None:
				self.fields['producto'] = forms.ModelChoiceField(label="Producto", queryset=opciones, empty_label=None)
				self.fields['producto'].initial = producto

				cantidad_field = self.fields['cantidad'] = forms.DecimalField(max_digits=10, decimal_places=4)

				if producto.seguimiento:
					opciones = almacen.codigos_lotes_producto(producto)
					self.fields['codigo_lote'] = forms.ChoiceField(label='Código de lote/serie', choices=opciones)

					if codigo_lote:
						self.fields['codigo_lote'].initial = codigo_lote
						cantidad_query = Q(control_stock__producto=producto, lote_produccion__codigo=codigo_lote)
					else:
						cantidad_query = Q(control_stock__producto=producto, lote_produccion__codigo=opciones[0][0])
						self.fields['codigo_lote'].initial = opciones[0][0]

					if producto.seguimiento == 2:
						cantidad_field.required = False
						cantidad_field.widget = forms.HiddenInput()
				else:
					cantidad_query = Q(control_stock__producto=producto)
			
				cantidad_min_value = -almacen.unidades_inventario_actuales.get(cantidad_query).cantidad_producto

				cantidad_field.validators.append(MinValueValidator(cantidad_min_value))
				cantidad_field.validators.append(MenorQueCeroValidator)

				cantidad_field.label = "Cantidad (mínimo "+str(cantidad_min_value)+')'

			else:
				self.fields['producto'] = forms.ModelChoiceField(label="Producto", queryset=opciones)

		self.order_fields(['almacen', 'categorias', 'producto', 'codigo_lote', 'cantidad', 'descripcion'])

	def clean_categorias(self):
		pass

	def save(self):
		almacen = self.cleaned_data['almacen']
		producto = self.cleaned_data['producto']

		cantidad = self.cleaned_data.get('cantidad')
		if not cantidad or producto.seguimiento == 2:
			cantidad = -1

		if producto.seguimiento:
			codigo_lote = self.cleaned_data.get('codigo_lote')
			unidad_inventario = almacen.unidades_inventario_actuales.get(control_stock__producto=producto, lote_produccion__codigo=codigo_lote)
		else:
			unidad_inventario = almacen.unidades_inventario_actuales.get(control_stock__producto=producto)

		ajuste_inventario = super().save(commit=False)
		ajuste_inventario.unidad_inventario = unidad_inventario
		ajuste_inventario.cantidad = cantidad
		ajuste_inventario.save()

		return ajuste_inventario

	class Meta:
		model = AjusteInventarioProducto
		fields = ['descripcion']
		labels = {
			'descripcion': ('Descripción')
		}



class FabricacionLoteForm(forms.Form):

	def __init__(self, almacen, componente, opciones, cantidad_componente, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['almacen'] = forms.ModelChoiceField(label="Almacén", queryset=Almacen.objects.actuales())
		self.fields['almacen'].initial = almacen
		self.fields['almacen'].widget = forms.HiddenInput()

		self.fields['componente'] = forms.ModelChoiceField(label="Componente", queryset=Producto.objects.actuales())
		self.fields['componente'].initial = componente
		self.fields['componente'].widget = forms.HiddenInput()

		self.fields['codigo_lote'] = forms.ChoiceField(label='Código de lote/serie', choices=opciones, required=True)

		cantidad_field = self.fields['cantidad'] = forms.DecimalField(max_digits=10, decimal_places=4, required=False)

		initials = kwargs.get('initial')

		if initials:
			codigo_lote = initials.get('codigo_lote')
			cantidad = initials.get('cantidad')

			self.fields['codigo_lote'].choices.append((codigo_lote, codigo_lote))
			self.fields['codigo_lote'].initial = codigo_lote
			self.fields['cantidad'].initial = cantidad

			cantidad_max_value = almacen.unidades_inventario_actuales.filter(control_stock__producto=componente, lote_produccion__codigo=codigo_lote).aggregate(cantidad_inventario=Sum('cantidad_producto'))['cantidad_inventario']
			cantidad_field.validators.append(MaxValueValidator(cantidad_max_value))
			cantidad_field.label = "Cantidad ("+str(cantidad_max_value)+' máximo)'

	def save(self, fabricacion):
		cantidad = self.cleaned_data['cantidad']
		unidad_inventario = self.cleaned_data['almacen'].unidades_inventario_actuales.get(control_stock__producto=self.cleaned_data['componente'], lote_produccion__codigo=self.cleaned_data['codigo_lote'])
		unidad_inventario.save()
		
		ajuste = AjusteInventarioProducto.objects.create(fabricacion=fabricacion, unidad_inventario=unidad_inventario, cantidad=-cantidad, descripcion='Fabricación {}'.format(fabricacion.id))
		return ajuste


class FabricacionLoteBaseFormSet(forms.BaseFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.componente = kwargs.get('form_kwargs').get('componente')
        self.cantidad_componente = kwargs.get('form_kwargs').get('cantidad_componente')
        self.titulo_form = 'Se necesita una cantidad de '+str(self.cantidad_componente)+' de '+str(self.componente)

    def clean(self):
    	restante = self.cantidad_componente

    	for form in self.forms:
    		cantidad = form.cleaned_data.get('cantidad')
    		if cantidad:
    			restante -= cantidad

    	if restante > 0:
    		raise forms.ValidationError('Se debe asignar una cantidad de '+str(restante)+' más de este componente para fabricar este producto.')
    	elif restante < 0:
    		raise forms.ValidationError('Se debe asignar una cantidad de '+str(-restante)+' menos de este componente para fabricar este producto.')

    def save(self, fabricacion):
    	for form in self.forms:
    		form.save(fabricacion)


class EliminarFabricacionForm(DeleteObjectForm):
	nombre_form = 'eliminar_fabricacion'
	model = Fabricacion

	def delete(self):
		fabricacion = self.cleaned_data['object_id']
		for ajuste in fabricacion.ajustes.all():
			ajuste.activo = False
			ajuste.save()
		super().delete()


class FabricacionForm(forms.ModelForm):
	titulo_form = 'fabricación'

	almacen_produccion = forms.ModelChoiceField(label="Almacén", queryset=Almacen.objects.actuales())
	fecha_produccion = forms.DateField(label="Fecha de producción", required=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.forms = []

		initials = kwargs.get('initial')

		if initials:
			almacen_id = initials.get('almacen_produccion')
			fecha_produccion = initials.get('fecha_produccion')
			fecha_vencimiento = initials.get('fecha_vencimiento')
			changed_data = initials.get('changed_data')

			if not changed_data:
				producto_id = initials.get('producto')
			elif changed_data != 'almacen_produccion':
				producto_id = initials.get('producto')
			else:
				producto_id = None
		else:
			almacen_id = self.data.get('almacen_produccion')
			producto_id = self.data.get('producto')
			fecha_produccion = self.data.get('fecha_produccion')
			fecha_vencimiento = self.data.get('fecha_vencimiento')

		user = RequestMiddleware(get_response=None).thread_local.current_request.user
		self.fields['almacen_produccion'].queryset = user.get_almacenes_perm('add_fabricacion').actuales()
		self.fields['fecha_produccion'].initial = fecha_produccion

		if almacen_id:
			almacen = Almacen.objects.get(id=almacen_id)

			opciones = almacen.opciones_fabricacion()
			
			if len(opciones['opciones']):
				self.fields['producto'] = forms.ChoiceField(label="Producto", choices=opciones['opciones'])

				if not producto_id:
					producto_id = opciones['opciones'][0][0]

				producto = Producto.objects.get(id=producto_id)
				self.fields['producto'].initial = producto

				cantidad_field = self.fields['cantidad_produccion'] = forms.DecimalField(max_digits=10, decimal_places=4)

				if producto.seguimiento == 2:
					cantidad_field.required = False
					cantidad_field.widget = forms.HiddenInput()
				elif producto.seguimiento:
					self.fields['codigo'] = forms.CharField(label='Código', required=False, max_length=255)
					self.fields['fecha_vencimiento'] = forms.DateField(label="Fecha de vencimiento", required=False)
					self.fields['fecha_vencimiento'].initial = fecha_vencimiento
				
				cantidad_max_value = opciones['cantidades_produccion_maxima'][int(producto_id)]

				cantidad_field.validators.append(MaxValueValidator(cantidad_max_value))
				cantidad_field.validators.append(MayorQueCeroValidator)

				cantidad_field.label = "Cantidad ("+str(cantidad_max_value)+' máximo)'
			else:
				self.fields['producto'] = forms.ChoiceField(label='Producto', choices=[('', '---------')])

		self.order_fields(['codigo', 'fecha_produccion', 'fecha_vencimiento', 'almacen_produccion', 'producto', 'cantidad_produccion'])


	def clean_producto(self):
		try:
			return Producto.objects.actuales().get(id=self.cleaned_data['producto'])
		except:
			raise forms.ValidationError('El producto no existe.')

	def clean_cantidad_produccion(self):
		producto = self.cleaned_data['producto']
		almacen = self.cleaned_data['almacen_produccion']
		control_stock = ControlStock.objects.filter(activo=True, producto=producto, almacen=almacen)
		
		if control_stock.exists():
			control_stock = control_stock[0]

			if control_stock.stock_maximo is not None:
				diferencia = self.cleaned_data['cantidad_produccion'] + almacen.cantidad_producto(producto) - control_stock.stock_maximo
				if diferencia > 0:
					raise forms.ValidationError('La cantidad total del producto en el almacén supera su stock máximo por '+str(diferencia))
		return self.cleaned_data['cantidad_produccion']

	def save(self):
		codigo = self.cleaned_data.get('codigo')
		almacen = self.cleaned_data['almacen_produccion']
		producto = self.cleaned_data.get('producto')
		cantidad_produccion = self.cleaned_data['cantidad_produccion']

		getcontext().prec = 4

		if not codigo:
			codigo = Fabricacion.objects.filter(lote_produccion__producto=producto).count()+1

		lote_produccion = LoteProduccion.objects.create(codigo=codigo, producto=producto, fecha_vencimiento=self.cleaned_data.get('fecha_vencimiento'))

		fecha_produccion = self.cleaned_data.get('fecha_produccion')
		if not fecha_produccion:
			fecha_produccion = lote_produccion.fecha_creacion

		lote_produccion.fecha_produccion = fecha_produccion
		lote_produccion.save()

		control_stock = ControlStock.objects.get_or_create(almacen=almacen, producto=producto)[0]

		if not producto.seguimiento:
			unidad_inventario, creado = UnidadInventario.objects.get_or_create(control_stock=control_stock, lote_produccion=None, activo=True)
		else:
			unidad_inventario = UnidadInventario.objects.create(control_stock=control_stock, lote_produccion=lote_produccion, activo=True)

		fabricacion = super(FabricacionForm, self).save(commit=False)
		fabricacion.lote_produccion = lote_produccion
		fabricacion.cantidad_produccion = cantidad_produccion
		fabricacion.unidad_inventario = unidad_inventario
		fabricacion.save()

		for componente_id, cantidad_componente in producto.componentes_totales().items():
			componente = Producto.objects.get(id=componente_id)
			if not componente.seguimiento:
				cantidad = cantidad_componente * Decimal(cantidad_produccion)
				unidad_inventario = almacen.unidades_inventario_actuales.get(control_stock__producto=componente)
				unidad_inventario.save()

				AjusteInventarioProducto.objects.create(fabricacion=fabricacion, unidad_inventario=unidad_inventario, cantidad=-cantidad, descripcion='Fabricación {}'.format(fabricacion.id))
		
		return fabricacion

	class Meta:
		model = Fabricacion
		fields = ['fecha_produccion']

