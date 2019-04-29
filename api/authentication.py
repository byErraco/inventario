from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .models import TiendaToken


class TiendaAuthentication(TokenAuthentication):

    def get_token_from_auth_header(self, auth):
        auth = auth.split()
        if not auth or auth[0].lower() != b'api-key':
            return None

        if len(auth) == 1:
            raise AuthenticationFailed('Las credenciales de autenticación no se proveyeron.')
        elif len(auth) > 2:
            raise AuthenticationFailed('La llave no debe contener espacios.')

        try:
            return auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed('La llave no debe contener caracteres inválidos.')

    def authenticate(self, request):
        auth = get_authorization_header(request)
        token = self.get_token_from_auth_header(auth)

        if not token:
            token = request.GET.get('api-key', request.POST.get('api-key', None))

        if token:
            return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = TiendaToken.objects.get(llave=key, activo=True, tienda__activo=True)
        except TiendaToken.DoesNotExist:
            raise AuthenticationFailed('Llave inválida.')

        user = token.tienda
        return (user, token)