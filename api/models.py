import os
import binascii

from django.db import models

from inventario.models import RegistroModel

# Create your models here.


class TiendaToken(RegistroModel):
    llave = models.CharField(max_length=40)
    tienda = models.ForeignKey('tiendas.Tienda', on_delete=models.CASCADE, related_name='token')

    def save(self, *args, **kwargs):
        if not self.llave:
            self.llave = self.generar_llave()
        return super(TiendaToken, self).save(*args, **kwargs)

    def generar_llave(self):
        return binascii.hexlify(os.urandom(20)).decode()

    class Meta(RegistroModel.Meta):
        verbose_name = 'llave de tienda'
        verbose_name_plural = 'llaves de tiendas'
        db_table = 'tienda_token'
