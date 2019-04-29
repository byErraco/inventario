from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView

from .tokens import account_activation_token
from .models import User


class ActivarUsuarioView(View):
	def get(self, request, uidb64, token):
		try:
			uid = urlsafe_base64_decode(uidb64).decode()
			usuario = User.objects.get(pk=uid)
		except(TypeError, ValueError, OverflowError, User.DoesNotExist):
			usuario = None

		if usuario is not None and account_activation_token.check_token(usuario, token):
			form = SetPasswordForm(usuario)
			return render(request, 'usuarios/reiniciar_contraseña.html', {'form': form, 'validlink': True})
		return render(request, 'usuarios/reiniciar_contraseña.html', {})

	def post(self, request, uidb64, token):
		try:
			uid = urlsafe_base64_decode(uidb64).decode()
			usuario = User.objects.get(pk=uid)
		except(TypeError, ValueError, OverflowError, User.DoesNotExist):
			usuario = None

		if usuario is not None and account_activation_token.check_token(usuario, token):
			form = SetPasswordForm(usuario, request.POST or None)

			if form.is_valid():
				usuario.is_active = True
				usuario.save()
				form.save()
				return redirect('usuarios:contraseña_establecida')
			return render(request, 'usuarios/reiniciar_contraseña.html', {'form': form, 'validlink': True})

		return render(request, 'usuarios/reiniciar_contraseña.html', {})


class BienvenidaView(LoginRequiredMixin, TemplateView):
	template_name = 'usuarios/bienvenida.html'


class ContraseñaEstablecidaView(TemplateView):
	template_name = 'usuarios/contraseña_establecida.html'


class IniciarSesionView(LoginView):
	template_name = 'usuarios/iniciar_sesion.html'


class ContraseñaOlvidadaView(PasswordResetView):
	template_name = 'usuarios/contraseña_olvidada.html'
	email_template_name = 'usuarios/correos/contraseña_olvidada_email.html'
	subject_template_name = 'usuarios/correos/contraseña_olvidada_asunto_email.txt'
	success_url = reverse_lazy('usuarios:contraseña_olvidada_email_enviado')


class ContraseñaOlvidadaEmailEnviadoView(PasswordResetDoneView):
	template_name = 'usuarios/contraseña_olvidada_email_enviado.html'


class ReiniciarContraseñaView(PasswordResetConfirmView):
	template_name = 'usuarios/reiniciar_contraseña.html'
	success_url = reverse_lazy('usuarios:contraseña_establecida')


