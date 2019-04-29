# Generated by Django 2.0.6 on 2018-12-01 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('almacenes', '0003_auto_20181026_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preciounidadinventario',
            name='base_imponible',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='preciounidadinventario',
            name='impuesto',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='impuesto'),
        ),
        migrations.AlterField(
            model_name='preciounidadinventario',
            name='margen_ganancia',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True, verbose_name='margen de ganancia'),
        ),
        migrations.AlterField(
            model_name='preciounidadinventario',
            name='porcentaje_impuesto',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='porcentaje de impuesto'),
        ),
        migrations.AlterField(
            model_name='preciounidadinventario',
            name='precio_venta_publico',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='precio final'),
        ),
    ]