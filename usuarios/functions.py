from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .tokens import account_activation_token


def enviar_email_activacion_usuario(user):
	if not user.is_active:
		current_site = Site.objects.get_current()
		mail_subject = 'Activar su cuenta de '+current_site.name+'.'
		message = render_to_string('usuarios/correos/activar_usuario_email.html', {
		                'user': user,
		                'domain': current_site.domain,
		                'site_name': current_site.name,
		                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
		                'token':account_activation_token.make_token(user),
		            })
		to_email = user.email
		email = EmailMessage(mail_subject, message, to=[to_email])
		return email.send()
	return 0