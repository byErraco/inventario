# Generated by Django 2.0.6 on 2018-10-17 03:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tiendas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiendatoken',
            name='tienda',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='token', to='tiendas.Tienda'),
        ),
        migrations.AddField(
            model_name='tiendatoken',
            name='ultimo_usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_api_tiendatoken', to=settings.AUTH_USER_MODEL, verbose_name='modificado la última vez por'),
        ),
    ]