# Generated by Django 2.0.6 on 2018-10-17 03:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Almacen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=255)),
                ('direccion', models.CharField(blank=True, max_length=255, null=True, verbose_name='dirección')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_almacen', 'Can see almacenes'),),
                'verbose_name_plural': 'almacenes',
                'verbose_name': 'almacén',
                'abstract': False,
                'db_table': 'almacen',
            },
        ),
        migrations.CreateModel(
            name='LoteProduccion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('codigo', models.CharField(max_length=255)),
                ('fecha_produccion', models.DateField(null=True)),
                ('fecha_vencimiento', models.DateField(null=True)),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_loteproduccion', 'Can see lotes produccion'),),
                'db_table': 'lote_produccion',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PrecioUnidadInventario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('base_imponible', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('margen_ganancia', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='margen de ganancia')),
                ('porcentaje_impuesto', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='porcentaje de impuesto')),
                ('impuesto', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='impuesto')),
                ('precio_venta_publico', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='precio final')),
                ('exento', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'verbose_name_plural': 'precios',
                'abstract': False,
                'verbose_name': 'precio',
                'db_table': 'precio_unidad_inventario',
            },
        ),
        migrations.CreateModel(
            name='UnidadInventario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('cantidad_producto', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Cantidad de producto')),
                ('fecha_ultima_sincronizacion', models.DateTimeField(null=True, verbose_name='fecha de última sincronización')),
                ('almacen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_inventario', to='almacenes.Almacen')),
                ('lote_produccion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unidades_inventario', to='almacenes.LoteProduccion')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_unidadinventario', 'Can see unidades inventario'),),
                'verbose_name_plural': 'unidades de inventario',
                'verbose_name': 'unidad de inventario',
                'abstract': False,
                'db_table': 'unidad_inventario',
            },
        ),
    ]
