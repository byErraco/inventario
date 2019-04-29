from django import forms
from django.utils.translation import gettext as _

from inventario.forms import DeleteObjectForm
from almacenes.models import UnidadInventario, ControlStock, Almacen
from personas.models import Persona 

from .models import Producto, CategoriaProducto, ComponenteProducto, ProveedorProducto, AtributoProducto, AtributoCategoria, Unidad


class UnidadForm(forms.ModelForm):
	nombre_form = 'crear_unidad'
	titulo_form = 'unidad'

	def clean_nombre(self):
		nombre = self.cleaned_data['nombre']
		if len(Unidad.objects.actuales().filter(nombre=nombre)) > 0:
			raise forms.ValidationError(_('Existe una unidad con este nombre.'))
		return nombre

	def clean_descripcion(self):
		descripcion = self.cleaned_data['descripcion']
		if len(Unidad.objects.actuales().filter(descripcion=descripcion)) > 0:
			raise forms.ValidationError(_('Existe una unidad con esta descripción.'))
		return descripcion
		
	class Meta:
		model = Unidad
		fields = ['nombre', 'descripcion']
		labels = {'descripcion': ('Descripción')}


class EliminarUnidadForm(DeleteObjectForm):
	nombre_form = 'eliminar_unidad'
	model = Unidad


class EliminarProductoForm(DeleteObjectForm):
	nombre_form = 'eliminar_producto'
	model = Producto


class EliminarCategoriaProductoForm(DeleteObjectForm):
	nombre_form = 'eliminar_categoria_producto'
	model = CategoriaProducto


class CategoriaProductoForm(forms.ModelForm):
	nombre_form = 'actualizar_categoria'
	titulo_form = 'categoría'

	def save(self, cambiar_slug=True):
		categoria = super(CategoriaProductoForm, self).save(commit=False)

		if cambiar_slug:
			categoria.slug = categoria.get_unique_slug()

		categoria.save()

		atributo_categoria = AtributoCategoria.objects.create(nombre=categoria.nombre, categoria=categoria)

		return categoria

	def clean(self):
		cleaned_data = super(CategoriaProductoForm, self).clean()

		if self.instance.nombre != cleaned_data['nombre']:
			if len(CategoriaProducto.objects.actuales().filter(nombre=cleaned_data['nombre'])) > 0:
				raise forms.ValidationError({'nombre': _('Existe una categoría con este nombre.')})

		return cleaned_data

	class Meta:
		model = CategoriaProducto
		fields = ['nombre']


class AgregarAtributoCategoriaForm(forms.ModelForm):
	nombre_form = 'agregar_atributo_categoria'

	def __init__(self, categoria,  *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['categoria'].initial =  categoria

	def save(self):
		atributo_categoria = super(AgregarAtributoCategoriaForm, self).save(commit=False)
		atributo_categoria.save()

		for producto in atributo_categoria.categoria.productos_actuales:
			AtributoProducto.objects.create(producto=producto, atributo_categoria=atributo_categoria)

		return atributo_categoria

	def clean(self):
		cleaned_data = super(AgregarAtributoCategoriaForm, self).clean()

		if len(AtributoCategoria.objects.actuales().filter(nombre=cleaned_data['nombre'], categoria=cleaned_data['categoria'])) > 0:
			raise forms.ValidationError({'nombre': _('Existe en esta categoría un atributo con este nombre.')})

		return cleaned_data

	class Meta:
		model = AtributoCategoria
		fields = ['categoria', 'nombre']
		widgets = {
			'categoria': forms.HiddenInput()
		}


class EliminarAtributoCategoriaForm(forms.ModelForm):
	nombre_form = 'eliminar_atributo_categoria'

	def delete(self):
		atributo = super(EliminarAtributoCategoriaForm, self).save(commit=False)
		atributo.activo = False
		atributo.save()

		return atributo

	class Meta:
		model = AtributoCategoria
		fields = ['nombre']
		widgets = {
			'nombre': forms.HiddenInput(),
		}


class ProductoForm(forms.ModelForm):
	nombre_form = 'actualizar_producto'
	titulo_form = 'producto'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		if UnidadInventario.objects.filter(control_stock__producto=self.instance, activo=True).exists():
			self.fields['unidad'].disabled =  True
			self.fields['balanza'].disabled =  True
			self.fields['seguimiento'].disabled =  True
			self.fields['producto_pre_fabricado'].disabled = True

		self.fields['unidad'].queryset = self.fields['unidad'].queryset.filter(activo=True)


	def save(self, cambiar_slug=True, commit=True):
		producto = super(ProductoForm, self).save(commit=False)

		if cambiar_slug:
			producto.slug = producto.get_unique_slug()
			
		if commit:
			producto.save()

		return producto

	def clean(self):
		cleaned_data = super(ProductoForm, self).clean()

		if self.instance.codigo_venta != cleaned_data['codigo_venta']:
			if len(Producto.objects.actuales().filter(codigo_venta=cleaned_data['codigo_venta'])) > 0:
				raise forms.ValidationError({'codigo_venta': _('Existe un producto con este código.')})
		if self.instance.descripcion != cleaned_data['descripcion']:
			if len(Producto.objects.actuales().filter(descripcion=cleaned_data['descripcion'])) > 0:
				raise forms.ValidationError({'descripcion': _('Existe un producto con esta descripcion.')})

		return cleaned_data

	class Meta:
		model = Producto
		fields = ['codigo_venta', 'descripcion', 'unidad', 'balanza', 
				  'producto_pre_fabricado', 'seguimiento']


class ActualizarAtributoProductoForm(forms.ModelForm):
	nombre_form = 'actualizar_atributo'

	def save(self):
		atributo_producto = super(ActualizarAtributoProductoForm, self).save(commit=False)

		atributo_producto_anterior = AtributoProducto.objects.get(pk=atributo_producto.pk)
		atributo_producto_anterior.activo = False
		atributo_producto_anterior.save()

		atributo_producto.pk = None
		atributo_producto.save()

		return atributo_producto

	class Meta:
		model = AtributoProducto
		fields = ['producto', 'atributo_categoria', 'valor']
		labels = {
            'valor': ('')
        }
		widgets = {
			'producto': forms.HiddenInput(),
			'atributo_categoria': forms.HiddenInput()
        }


class ActualizarComponenteProductoForm(forms.ModelForm):
	nombre_form = 'actualizar_componente'

	def save(self):
		componente_producto = super(ActualizarComponenteProductoForm, self).save(commit=False)

		componente_producto_anterior = ComponenteProducto.objects.get(pk=componente_producto.pk)
		componente_producto_anterior.activo = False
		componente_producto_anterior.save()

		componente_producto.pk = None
		componente_producto.save()

		return componente_producto

	class Meta:
		model = ComponenteProducto
		fields = ['producto_base', 'producto_componente', 'cantidad_componente']
		labels = {
            'cantidad_componente': ('')
        }
		widgets = {
			'producto_base': forms.HiddenInput(),
			'producto_componente': forms.HiddenInput()
        }


class AgregarCategoriaProductoForm(forms.Form):
	nombre_form = 'agregar_categoria'

	def __init__(self, producto,  *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto'] = forms.ModelChoiceField(queryset=Producto.objects.all())
		self.fields['producto'].initial =  producto
		self.fields['producto'].widget = forms.HiddenInput()
		self.fields['categoria'] = forms.ModelChoiceField(label='Categoría', queryset=producto.opciones_para_categorias, empty_label=None)

	def save(self):
		atributos_categoria = self.cleaned_data['categoria'].atributos_actuales

		for atributo_categoria in atributos_categoria:
			AtributoProducto.objects.create(producto=self.cleaned_data['producto'], atributo_categoria=atributo_categoria)


class AgregarControlStockForm(forms.ModelForm):
	nombre_form = 'agregar_control_stock'

	def __init__(self, producto,  *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto'].initial =  producto
		self.fields['almacen'].queryset = Almacen.objects.opciones_para_control_stock(producto)

	class Meta:
		model = ControlStock
		fields = ['producto', 'almacen', 'stock_minimo', 'stock_maximo']
		widgets = {
			'producto': forms.HiddenInput()
		}


class ActualizarControlStockForm(forms.ModelForm):
	nombre_form = 'actualizar_control_stock'

	def __init__(self, *args, **kwargs):
		disabled = kwargs.pop('disabled', None)

		super().__init__(*args, **kwargs)

		self.fields['control_stock'] = forms.IntegerField(initial=kwargs.get('instance').id, widget=forms.HiddenInput())

		if disabled:
			self.disabled = True
			self.fields['stock_minimo'].disabled = True
			self.fields['stock_maximo'].disabled = True

	class Meta:
		model = ControlStock
		fields = ['producto', 'almacen', 'stock_minimo', 'stock_maximo']
		widgets = {
			'producto': forms.HiddenInput(),
			'almacen': forms.HiddenInput()
		}


class AgregarComponenteProductoForm(forms.ModelForm):
	nombre_form = 'agregar_componente'

	def clean(self):
		cleaned_data = super().clean()

		if cleaned_data['producto_componente'] not in cleaned_data['producto_base'].opciones_para_componentes:
			raise forms.ValidationError({'producto_componente': _('El componente no puede ser asignado.')})

		return cleaned_data

	def __init__(self, producto,  *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto_base'].initial =  producto
		self.fields['producto_componente'] = forms.ModelChoiceField(label='Componente', queryset=producto.opciones_para_componentes, empty_label=None)

	class Meta:
		model = ComponenteProducto
		fields = ['producto_base', 'producto_componente', 'cantidad_componente']
		labels = {
			'cantidad_componente': (''),
		}
		widgets = {
			'producto_base': forms.HiddenInput()
		}


class AgregarProveedorProductoForm(forms.ModelForm):
	nombre_form = 'agregar_proveedor'

	def __init__(self, producto,  *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto'].initial =  producto
		self.fields['proveedor'] = forms.ModelChoiceField(queryset=producto.opciones_para_proveedores, empty_label=None)

	class Meta:
		model = ProveedorProducto
		fields = ['producto', 'proveedor']
		widgets = {
			'producto': forms.HiddenInput()
		}


class EliminarComponenteProductoForm(forms.Form):
	nombre_form = 'eliminar_componente' 

	def __init__(self, producto,  componente, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto_base'] = forms.ModelChoiceField(queryset=Producto.objects.all())
		self.fields['producto_componente'] = forms.ModelChoiceField(queryset=Producto.objects.all())

		self.fields['producto_base'].widget = forms.HiddenInput()
		self.fields['producto_componente'].widget = forms.HiddenInput()

		self.fields['producto_base'].initial =  producto
		self.fields['producto_componente'].initial =  componente

	def delete(self):
		componente_producto = ComponenteProducto.objects.actuales().get(producto_base=self.cleaned_data['producto_base'], producto_componente=self.cleaned_data['producto_componente'])
		componente_producto.activo = False
		componente_producto.save()


class EliminarAtributosProductoForm(forms.Form):
	nombre_form = 'eliminar_atributos'

	def __init__(self, producto,  categoria, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto'] = forms.ModelChoiceField(queryset=Producto.objects.all())
		self.fields['categoria'] = forms.ModelChoiceField(queryset=CategoriaProducto.objects.all())

		self.fields['producto'].widget = forms.HiddenInput()
		self.fields['categoria'].widget = forms.HiddenInput()

		self.fields['producto'].initial =  producto
		self.fields['categoria'].initial =  categoria

	def delete(self):
		atributos = self.cleaned_data['producto'].atributos_actuales_por_categoria(self.cleaned_data['categoria'])

		for atributo in atributos:
			atributo.activo = False
			atributo.save()


class EliminarProveedorProductoForm(forms.Form):
	nombre_form = 'eliminar_proveedor'

	def __init__(self, producto,  proveedor, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['producto'] = forms.ModelChoiceField(queryset=Producto.objects.all())
		self.fields['proveedor'] = forms.ModelChoiceField(queryset=Persona.objects.all())

		self.fields['producto'].widget = forms.HiddenInput()
		self.fields['proveedor'].widget = forms.HiddenInput()

		self.fields['producto'].initial =  producto
		self.fields['proveedor'].initial =  proveedor

	def delete(self):
		proveedor_producto = self.cleaned_data['producto'].proveedores_producto.get(activo=True, proveedor=self.cleaned_data['proveedor'])
		proveedor_producto.activo = False
		proveedor_producto.save()