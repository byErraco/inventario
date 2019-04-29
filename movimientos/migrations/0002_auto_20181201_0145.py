# Generated by Django 2.0.6 on 2018-12-01 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movimientos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compraproducto',
            name='costo_unidad',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='trasladoproducto',
            name='costo',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
