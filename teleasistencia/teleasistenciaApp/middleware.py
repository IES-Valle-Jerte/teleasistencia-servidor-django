import jwt
from jwt.exceptions import InvalidTokenError

from django.conf import settings
from django.contrib.auth.models import User

from .models import Logs_AccionesUsuarios, Logs_ConexionesUsuarios
from utilidad.logging import info, yellow

class LoggingMiddleware:
    """
    Middleware encargado de loggear
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la petición
        response = self.get_response(request)
        # Si la petición está correctamente autorizada, loggearemos lo correspondiente
        _log_request(request, response)
        # En caso de no estar autorizado, el SecurityMiddleware habrá dado una respuesta adecuada
        return response


def _log_request(request, response):
        # Si es una petición a la API REST, lo registramos en Logs_AccionesUsuarios
        if request.user.pk is not None and request.path.startswith('/api-rest/'):
            # Sacamos datos del usuario autorizado
            if _extract_user(request):
                # Crear el log
                log = Logs_AccionesUsuarios(
                    direccion_ip=request.META.get('REMOTE_ADDR'),
                    user=request.user,
                    ruta=request.path,
                    query=request.scope['query_string'].decode(),
                    metodo_http=request.method,
                    estado_http=response.status_code,
                )

                log.save()  # Guardar el log en la BBDD
                yellow("LoggingMiddleware", str(log))

        # Si es para un inicio de sesión, lo registramos en Logs_Sesiones
        # Registraremos cualquier tipo de inicio de sesión
        elif request.path.startswith(('/admin/login', '/api/token', '/api-auth')):
            # Crear el log
            log = Logs_ConexionesUsuarios(
                direccion_ip=request.META.get('REMOTE_ADDR'),
                username=request.POST.get('username'),
            )

            path = request.path

            # Logins del panel de administración
            if path.startswith('/admin/login'):
                log.tipo_login = log.TIPO_LOGIN_ENUM.PANEL_ADMIN
                log.login_correcto = (response.status_code == 302)
            # Logins por token
            elif path.startswith('/api/token'):
                log.tipo_login = log.TIPO_LOGIN_ENUM.TOKEN_API
                log.login_correcto = (response.status_code == 200)
            # Otros
            else:
                log.tipo_login = log.TIPO_LOGIN_ENUM.OTRO

            if log.username is not None:
                log.save()  # Guardar el log en la BBDD
                yellow("LoggingMiddleware", str(log))


def _extract_user(request):
    """
    Intenta extraer, a partir del campo "user_id" del token de autorización, el usuario
    de la BBDD y lo guardamos internamente en la petición para propositos de logging.

    Devuelve True o False dependiendo de si el token era válido o no.
    """
    try:
        jwt_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        # Descifrar el token y sacar el ID de usuario
        payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Guardar el usuario si lo hemos conseguido extraer
        request.user = User.objects.get(id=user_id)
        return True
    except InvalidTokenError | IndexError:
        return False
