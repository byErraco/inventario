from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
	ActivarUsuarioView, IniciarSesionView,
	ContraseñaOlvidadaView, ContraseñaOlvidadaEmailEnviadoView,
	ReiniciarContraseñaView, ContraseñaEstablecidaView
	)

app_name = "usuarios"

urlpatterns = [
	path('activar/<uidb64>/<token>', ActivarUsuarioView.as_view(), name='activar'),
	path('contraseña_establecida/', ContraseñaEstablecidaView.as_view(), name='contraseña_establecida'),
	path('iniciar_sesion/', IniciarSesionView.as_view(), name='iniciar_sesion'),
	path('cerrar_sesion/', auth_views.logout_then_login, name='cerrar_sesion'),
	path('contraseña_olvidada/', ContraseñaOlvidadaView.as_view(), name='contraseña_olvidada'),
	path('contraseña_olvidada_email_enviado/', ContraseñaOlvidadaEmailEnviadoView.as_view(), name='contraseña_olvidada_email_enviado'),
	path('reiniciar_contraseña/<uidb64>/<token>', ReiniciarContraseñaView.as_view(), name='reiniciar_contraseña'),
]