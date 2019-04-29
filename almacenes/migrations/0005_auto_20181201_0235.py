# Generated by Django 2.0.6 on 2018-12-01 06:35

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def agregar_control_stock(apps, schema_editor):
    UnidadInventario = apps.get_model('almacenes', 'UnidadInventario')
    ControlStock = apps.get_model('almacenes', 'ControlStock')

    for unidad_inventario in UnidadInventario.objects.all():
        control_stock = ControlStock.objects.get_or_create(producto=unidad_inventario.producto, almacen=unidad_inventario.almacen)[0]
        unidad_inventario.control_stock = control_stock
        unidad_inventario.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('productos', '0001_initial'),
        ('almacenes', '0004_auto_20181201_0145'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('stock_minimo', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10, verbose_name='stock mínimo')),
                ('stock_maximo', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10, verbose_name='stock máximo')),
                ('almacen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='almacenes.Almacen')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='productos.Producto')),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_almacenes_controlstock', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
            ],
            options={
                'permissions': (('view_', 'Can see controles de stock'),),
                'verbose_name': 'control de stock',
                'abstract': False,
                'db_table': 'control_stock',
                'verbose_name_plural': 'controles de stock',
                'ordering': ['-fecha_ultima_modificacion', '-id'],
            },
        ),
        migrations.CreateModel(
            name='InventarioFisico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_almacenes_inventariofisico', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
            ],
            options={
                'permissions': (('view_inventariofisico', 'Can see inventarios físicos'),),
                'verbose_name': 'inventario físico',
                'abstract': False,
                'db_table': 'inventario_fisico',
                'verbose_name_plural': 'inventarios físicos',
                'ordering': ['-fecha_ultima_modificacion', '-id'],
            },
        ),
        migrations.CreateModel(
            name='UnidadInventarioFisico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de última modificación')),
                ('activo', models.BooleanField(default=True)),
                ('inventario_fisico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_inventario_fisico', to='almacenes.InventarioFisico')),
                ('ultimo_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_almacenes_unidadinventariofisico', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por')),
            ],
            options={
                'verbose_name': 'unidad inventario físico',
                'abstract': False,
                'db_table': 'unidad_inventario_fisico',
                'verbose_name_plural': 'unidades inventario físico',
                'ordering': ['-fecha_ultima_modificacion', '-id'],
            },
        ),
        migrations.AddField(
            model_name='unidadinventariofisico',
            name='unidad_inventario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_inventarios_fisicos', to='almacenes.UnidadInventario'),
        ),
        migrations.AddField(
            model_name='unidadinventario',
            name='control_stock',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unidades_inventario', to='almacenes.ControlStock'),
        ),
        migrations.RunPython(agregar_control_stock),
        migrations.AlterField(
            model_name='unidadinventario',
            name='control_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_inventario', to='almacenes.ControlStock'),
        ),
        migrations.RemoveField(
            model_name='unidadinventario',
            name='almacen',
        ),
        migrations.RemoveField(
            model_name='unidadinventario',
            name='producto',
        ),
    ]