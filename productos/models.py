from decimal import getcontext, Decimal, ROUND_DOWN

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.text import slugify

from inventario.models import RegistroModel, RegistroQuerySet, ChoiceEnum
from personas.models import Persona
from tiendas.models import Tienda
from movimientos.models import CompraProducto

# Create your models here.


class ProductoQuerySet(RegistroQuerySet):
	def fabricados(self):
		return self.filter(id__in=ComponenteProducto.objects.actuales().values_list('producto_base', flat=True)).distinct()

	def no_fabricados(self):
		return self.exclude(id__in=ComponenteProducto.objects.actuales().values_list('producto_base', flat=True)).distinct()

	def pre_fabricados(self):
		return self.filter(producto_pre_fabricado=True, id__in=ComponenteProducto.objects.actuales().values_list('producto_base', flat=True)).distinct()


class Producto(RegistroModel):
	class PeriodoVenta(ChoiceEnum):
		DIARIO = 1, 'diario'
		SEMANAL = 2, 'semanal'

	class Seguimiento(ChoiceEnum):
		LOTE = 1, 'lote'
		SERIE = 2, 'número de serie'

	codigo_venta = models.CharField(max_length=45, verbose_name='código de venta')
	descripcion = models.CharField(max_length=45, verbose_name='descripción')
	unidad = models.ForeignKey('productos.Unidad', blank=True, null=True, on_delete=models.SET_NULL, related_name='productos')
	balanza = models.BooleanField(default=False)
	producto_pre_fabricado = models.BooleanField(default=False, verbose_name='producto pre-fabricado')
	limite_venta_persona = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=4, verbose_name='límite de venta por persona')
	periodo_venta_producto = models.SmallIntegerField(blank=True,
		null=True, 
		choices=PeriodoVenta.choices(),
		verbose_name='periodo del límite de venta'
		)
	seguimiento = models.SmallIntegerField(blank=True,
		null=True,
		choices=Seguimiento.choices(),
		verbose_name='tipo de seguimiento'
		)
	atributos_categoria = models.ManyToManyField('AtributoCategoria', through='AtributoProducto')
	componentes = models.ManyToManyField('self',
		through='ComponenteProducto',
		through_fields=('producto_base', 'producto_componente'),
		symmetrical=False
		)
	proveedores = models.ManyToManyField('personas.Persona', through='ProveedorProducto')
	slug = models.SlugField(unique=True)

	objects = ProductoQuerySet.as_manager()

	def seguimiento_str(self):
		return str(self.Seguimiento(self.seguimiento))
	
	def periodo_venta_producto_str(self):
		return str(self.PeriodoVenta(self.periodo_venta_producto))

	@property
	def categorias_actuales(self):
		return CategoriaProducto.objects.actuales().filter(id__in=self.atributos_categoria_actuales.values_list('categoria', flat=True).distinct())

	@property
	def atributos_por_categorias_actuales(self):
		atributos = {}
		for categoria in self.categorias_actuales:
			atributos[categoria.nombre] = []

		for categoria in self.categorias_actuales:
			for atributo in self.atributos_actuales.filter(atributo_categoria__activo=True, atributo_categoria__categoria=categoria):
				atributos[categoria.nombre].append(atributo)

		return atributos

	def atributos_actuales_por_categoria(self, categoria):
		return self.atributos_actuales.filter(atributo_categoria__activo=True, atributo_categoria__categoria=categoria)

	@property
	def precios_tiendas_actuales(self):
		return self.precios_tiendas.filter(tienda__activo=True, activo=True)

	@property
	def componentes_actuales(self):
		return self.componentes.filter(activo=True, id__in=self.componentes_producto.filter(activo=True).values_list('producto_componente', flat=True)).distinct()

	@property
	def productos_compuestos_actuales(self):
		return self.compuestos.filter(activo=True)

	@property
	def componentes_producto_actuales(self):
		return self.componentes_producto.filter(producto_componente__activo=True, activo=True)

	@property
	def proveedores_actuales(self):
		return self.proveedores.filter(activo=True, id__in=self.proveedores_producto.filter(activo=True).values_list('proveedor', flat=True)).distinct()
	
	@property
	def tiendas_actuales(self):
		return self.tiendas.filter(activo=True, id__in=self.precios_tiendas.filter(activo=True).values_list('tienda', flat=True)).distinct()

	@property
	def atributos_actuales(self):
		return self.atributos.filter(atributo_categoria__activo=True, activo=True)

	@property
	def atributos_categoria_actuales(self):
		return self.atributos_categoria.filter(activo=True, id__in=self.atributos_actuales.values_list('atributo_categoria', flat=True))

	def fabricado_property(self):
		return len(self.componentes_producto_actuales) > 0
	fabricado_property.boolean = True
	fabricado_property.short_description = 'fabricado'
	
	fabricado = property(fabricado_property)

	def componentes_totales(self, filtro=models.Q(), componentes_totales=None, cantidad_componente=1):
		if componentes_totales is None:
			componentes_totales = {}

		for componente_producto in self.componentes_producto_actuales.filter(filtro):

			componente = componente_producto.producto_componente
			if componente.fabricado and not componente.producto_pre_fabricado:
				componente.componentes_totales(filtro, componentes_totales, componente_producto.cantidad_componente)
			else: 
				if componente.id in componentes_totales.keys():
					componentes_totales[componente.id] += componente_producto.cantidad_componente*cantidad_componente
				else:
					componentes_totales[componente.id] = componente_producto.cantidad_componente*cantidad_componente
		return componentes_totales

	def compuestos_totales(self, lista):
		for compuesto in self.productos_compuestos_actuales:
			lista.append(compuesto.producto_base.id)
			Producto.objects.get(id=compuesto.producto_base.id).compuestos_totales(lista)

	def cantidad_produccion_maxima(self, almacen):
		getcontext().prec = 4
		getcontext().rounding = ROUND_DOWN

		componentes_totales = self.componentes_totales()
		cantidades_inventario = almacen.productos_actuales.filter(id__in=componentes_totales.keys()).annotate(cantidad_inventario=Coalesce(Sum('stocks__unidades_inventario__cantidad_producto'), 0))
		if not len(cantidades_inventario):
			return 0

		cantidad_produccion_maxima = getcontext().Emax 
		for componente_id, cantidad_componente in componentes_totales.items():
			cantidad_inventario = cantidades_inventario.filter(id=componente_id)
			if len(cantidad_inventario):
				cantidad_inventario = cantidad_inventario[0].cantidad_inventario
			else:
				return 0
			cantidad_produccion_maxima = min(cantidad_produccion_maxima, Decimal(cantidad_inventario / cantidad_componente))
		
		return cantidad_produccion_maxima

	@property
	def opciones_para_componentes(self):
		componentes = Producto.objects.actuales().exclude(id=self.id).exclude(id__in=self.componentes_actuales.values_list('id', flat=True))
		lista = []
		self.compuestos_totales(lista)
		componentes = componentes.exclude(id__in=lista)
		return componentes
	
	@property
	def opciones_para_proveedores(self):
		return Persona.objects.actuales().exclude(id__in=self.proveedores_actuales.values_list('id', flat=True))

	@property
	def opciones_para_categorias(self):
		return CategoriaProducto.objects.actuales().filter(id__in=AtributoCategoria.objects.actuales().values_list('categoria', flat=True)).exclude(id__in=self.categorias_actuales.values_list('id', flat=True))

	@property
	def opciones_para_precios_tiendas(self):
		return Tienda.objects.actuales().exclude(id__in=self.tiendas_actuales.values_list('id', flat=True))

	@property
	def ultima_compra(self):
		return CompraProducto.objects.actuales().filter(unidad_inventario__control_stock__producto=self).latest('fecha_creacion')
	
	def get_absolute_url(self):
		return reverse("productos:detalle_producto", kwargs={'slug': self.slug})

	def get_unique_slug(self):
		slug = slugify(self.descripcion)
		unique_slug = slug
		num = Producto.objects.filter(slug=unique_slug).count()

		if num > 0:
			unique_slug = '{}-{}'.format(slug, num)

		return unique_slug

	def __str__(self):
		return self.descripcion

	search_fields = ('codigo_venta', 'descripcion')
	
	class Meta(RegistroModel.Meta):
		db_table = 'producto'
		permissions = (
		        ('view_producto', 'Can see productos'),
		    )
			

class ComponenteProducto(RegistroModel):
	producto_base = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='componentes_producto')
	producto_componente = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='compuestos')
	cantidad_componente = models.DecimalField(max_digits=10, decimal_places=4)

	objects = RegistroQuerySet.as_manager()

	def __str__(self):
		return str(self.producto_base)+'_'+str(self.producto_componente)

	class Meta(RegistroModel.Meta):
		db_table = 'componente_producto'


class CategoriaProducto(RegistroModel):
	nombre = models.CharField(max_length=255)

	slug = models.SlugField(unique=True)

	objects = RegistroQuerySet.as_manager()

	@property
	def atributos_actuales(self):
		return self.atributos.filter(activo=True)

	@property
	def productos_actuales(self):
		return Producto.objects.actuales().filter(id__in=AtributoProducto.objects.actuales().filter(atributo_categoria__categoria=self, atributo_categoria__activo=True).values_list('producto', flat=True)).distinct()

	def get_absolute_url(self):
		return reverse("productos:detalle_categoria", kwargs={'slug': self.slug})

	def get_unique_slug(self):
		slug = slugify(self.nombre)
		unique_slug = slug
		num = CategoriaProducto.objects.filter(slug=unique_slug).count()

		if num > 0:
			unique_slug = '{}-{}'.format(slug, num)

		return unique_slug

	def __str__(self):
		return self.nombre

	search_fields = ('nombre',)

	class Meta(RegistroModel.Meta):
		db_table = 'categoria_producto'
		verbose_name = 'categoría'
		verbose_name_plural = 'categorías'
		ordering = ('nombre',)
		permissions = (
		        ('view_categoriaproducto', 'Can see categorías productos'),
		    )


class AtributoCategoria(RegistroModel):
	nombre = models.CharField(max_length=255)
	categoria = models.ForeignKey('productos.CategoriaProducto', on_delete=models.CASCADE, related_name='atributos')

	objects = RegistroQuerySet.as_manager()
		
	def __str__(self):
		return self.nombre+'_'+str(self.categoria)

	class Meta(RegistroModel.Meta):
		db_table = 'atributo_categoria'


class AtributoProducto(RegistroModel):
	producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='atributos')
	atributo_categoria = models.ForeignKey('productos.AtributoCategoria', on_delete=models.CASCADE, related_name='productos')
	valor = models.CharField(max_length=255)

	objects = RegistroQuerySet.as_manager()

	def __str__(self):
		return str(self.producto)+'_'+str(self.atributo_categoria)

	class Meta(RegistroModel.Meta):
		db_table = 'atributo_producto'


class Unidad(RegistroModel):
	nombre = models.CharField(max_length=255)
	descripcion = models.CharField(max_length=255)

	objects = RegistroQuerySet.as_manager()
		
	def __str__(self):
		return self.nombre

	search_fields = ('nombre', 'descripcion')

	class Meta(RegistroModel.Meta):
		db_table = 'unidad'
		verbose_name_plural = 'unidades'
		ordering = ('nombre',)
		permissions = (
		        ('view_unidad', 'Can see unidades'),
		    )


class ProveedorProducto(RegistroModel):
	producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='proveedores_producto')
	proveedor = models.ForeignKey('personas.Persona', on_delete=models.CASCADE, related_name='productos_proveedor')

	def __str__(self):
		return str(self.proveedor)+'_'+str(self.producto)

	class Meta(RegistroModel.Meta):
		db_table = 'proveedor_producto'