# Generated by Django 2.0.6 on 2018-10-17 03:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('personas', '0001_initial'),
        ('almacenes', '0002_auto_20181016_2356'),
    ]

    operations = [
        migrations.CreateModel(
            name='AjusteInventarioProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=10)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_ajusteinventarioproducto', 'Can see ajustes inventario producto'),),
                'verbose_name_plural': 'ajustes',
                'verbose_name': 'ajuste',
                'abstract': False,
                'db_table': 'ajuste_inventario_producto',
            },
        ),
        migrations.CreateModel(
            name='CompraProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=10)),
                ('costo_unidad', models.DecimalField(decimal_places=4, max_digits=10)),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compras_proveedor', to='personas.Persona')),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_compraproducto', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
                ('unidad_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compras', to='almacenes.UnidadInventario')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_compraproducto', 'Can see compras producto'),),
                'verbose_name_plural': 'compras',
                'verbose_name': 'compra',
                'abstract': False,
                'db_table': 'compra_producto',
            },
        ),
        migrations.CreateModel(
            name='CostoCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('descripcion', models.CharField(max_length=40, verbose_name='Descripción')),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=10)),
                ('compra_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costos', to='movimientos.CompraProducto')),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_costocompra', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'verbose_name_plural': 'costos adicionales',
                'abstract': False,
                'verbose_name': 'costo adicional',
                'db_table': 'costo_compra',
            },
        ),
        migrations.CreateModel(
            name='Fabricacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('cantidad_produccion', models.DecimalField(decimal_places=4, max_digits=10, null=True, verbose_name='cantidad')),
                ('lote_produccion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fabricacion', to='almacenes.LoteProduccion')),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_fabricacion', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
                ('unidad_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fabricaciones', to='almacenes.UnidadInventario')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_fabricacion', 'Can see fabricaciones'),),
                'verbose_name_plural': 'fabricaciones',
                'verbose_name': 'fabricación',
                'abstract': False,
                'db_table': 'fabricacion',
            },
        ),
        migrations.CreateModel(
            name='TrasladoProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=10)),
                ('costo', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('fecha_confirmacion', models.DateTimeField(null=True)),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_trasladoproducto', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
                ('unidad_inventario_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='traslados_destino', to='almacenes.UnidadInventario')),
                ('unidad_inventario_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='traslados_origen', to='almacenes.UnidadInventario')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_trasladoproducto', 'Can see traslados producto'), ('confirm_trasladoproducto', 'Can confirm traslado producto')),
                'verbose_name_plural': 'traslados',
                'verbose_name': 'traslado',
                'abstract': False,
                'db_table': 'traslado_producto',
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('estado', models.IntegerField(choices=[(0, 'En proceso'), (1, 'Finalizada'), (2, 'Pausada'), (3, 'Cancelada')])),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_venta', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'db_table': 'venta',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VentaProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=10)),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_ventaproducto', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
                ('unidad_inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas', to='almacenes.UnidadInventario')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='venta_productos', to='movimientos.Venta')),
            ],
            options={
                'ordering': ['-fecha_ultima_modificacion', '-id'],
                'permissions': (('view_ventaproducto', 'Can see ventas producto'),),
                'verbose_name_plural': 'ventas',
                'verbose_name': 'venta',
                'abstract': False,
                'db_table': 'venta_producto',
            },
        ),
        migrations.AddField(
            model_name='ajusteinventarioproducto',
            name='fabricacion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ajustes', to='movimientos.Fabricacion'),
        ),
        migrations.AddField(
            model_name='ajusteinventarioproducto',
            name='ultimo_usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_movimientos_ajusteinventarioproducto', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por'),
        ),
        migrations.AddField(
            model_name='ajusteinventarioproducto',
            name='unidad_inventario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ajustes', to='almacenes.UnidadInventario'),
        ),
    ]
