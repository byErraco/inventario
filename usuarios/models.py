from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

from almacenes.models import Almacen
from tiendas.models import Tienda


def has_almacen(self, almacen):
    return self.almacenes.filter(id=almacen.id).exists()

Group.add_to_class('almacenes', models.ManyToManyField('almacenes.Almacen', limit_choices_to={'activo': True}, blank=True, related_name='groups'))
Group.add_to_class('has_almacen', has_almacen)


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('El usuario necesita un email.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_staffuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    user_almacenes = models.ManyToManyField('almacenes.Almacen', limit_choices_to={'activo': True}, blank=True, related_name='usuarios', verbose_name='Almacenes')

    def __str__(self):
        return self.get_full_name()
        
    def get_full_name(self):
        try:
            fullname = self.persona.nombre
            if self.persona.apellido:
                fullname += ' '+self.persona.apellido
            return fullname
        except:
            return self.email
            
    def get_all_almacenes(self):
        if self.is_active:
            if self.is_superuser:
                return Almacen.objects.all()

            almacenes = self.user_almacenes.all()
            for group in self.groups.all():
                almacenes |= group.almacenes.all()
            return almacenes.distinct()
            
        return Almacen.objects.none()

    def get_all_tiendas(self, almacenes_activos=True):
        if self.is_active:
            if self.is_superuser:
                return Tienda.objects.all()

            if almacenes_activos:
                return Tienda.objects.filter(id__in=self.get_all_almacenes().filter(activo=True).values_list('tienda', flat=True))

            return Tienda.objects.filter(id__in=self.get_all_almacenes().values_list('tienda', flat=True))
            
        return Tienda.objects.none()

    def get_almacenes_perm(self, codename):
        if self.is_active:
            if self.is_superuser:
                return self.get_all_almacenes()

            if self.user_permissions.filter(codename=codename).exists():
                almacenes = self.user_almacenes.all()
            else:
                almacenes = Almacen.objects.none()
            for group in self.groups.all():
                if group.permissions.filter(codename=codename).exists():
                    almacenes |= group.almacenes.all()
            return almacenes.distinct()

        return Almacen.objects.none()
        
    def has_almacen(self, almacen):
        return self.get_all_almacenes().filter(id=almacen.id).exists()

    def _has_almacen(self, almacen):
        return self.user_almacenes.filter(id=almacen.id).exists()

    def has_almacen_perm(self, almacen, codename):
        if self.is_active:
            if self.is_superuser:
                return True
            if self._has_almacen(almacen) and self.user_permissions.filter(codename=codename).exists():
                return True
            for group in self.groups.all():
                if group.has_almacen(almacen) and group.permissions.filter(codename=codename).exists():
                    return True
        return False

    def has_model_perms(self, app_label, model):
        if self.is_active:
            if self.is_superuser:
                return True
            for perm in self.get_all_permissions():
                app, perm_model = perm.split('.')
                mod = perm_model[perm_model.index('_')+1:]
                if app == app_label and mod == model:
                    return True
        return False
