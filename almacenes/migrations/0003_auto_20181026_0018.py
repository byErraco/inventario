# Generated by Django 2.0.6 on 2018-10-26 04:18

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('almacenes', '0002_auto_20181016_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidadinventario',
            name='cantidad_producto',
            field=models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10, verbose_name='Cantidad de producto'),
        ),
    ]
