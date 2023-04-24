import jwt
from jwt.exceptions import InvalidTokenError

from django.conf import settings
from django.contrib.auth.models import User

from .models import Logs_AccionesUsuarios, Logs_ConexionesUsuarios
from utilidad.logging import info, error, yellow

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
        _extract_user(request)
        _log_request(request, response)

        # En caso de no estar autorizado, el SecurityMiddleware habrá dado una respuesta adecuada
        return response


def _log_request(request, response):
    path = request.path
    # ############### Acciones ############### #
    # Acciones realizadas en la Api-Rest
    if path.startswith('/api-rest') and request.user.pk is not None:
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

    # ################ Logins ################ #
    # Logins de la api-rest para obtener Token JWT
    elif path.startswith('/api/token'):
        # Manejar edgecase Postman VS App
        username = request.POST.get('username') \
            if request.user.pk is None \
            else request.user.username

        # Crear el log
        log = Logs_ConexionesUsuarios(
            direccion_ip=request.META.get('REMOTE_ADDR'),
            username=username,
            tipo_login=Logs_ConexionesUsuarios.TIPO_LOGIN_ENUM.TOKEN_API,
            login_correcto=(response.status_code == 200),
        )

        log.save()  # Guardar el log en la BBDD
        yellow("LoggingMiddleware", str(log))

    # Logins por panel de administración (las acciones se quedan registradas en otro lado)
    elif path.startswith('/admin/login') and request.method == "POST":
        # Crear el log
        log = Logs_ConexionesUsuarios(
            direccion_ip=request.META.get('REMOTE_ADDR'),
            username=request.POST.get('username'),
            tipo_login=Logs_ConexionesUsuarios.TIPO_LOGIN_ENUM.PANEL_ADMIN,
            login_correcto=(response.status_code == 302),
        )

        log.save()  # Guardar el log en la BBDD
        yellow("LoggingMiddleware", str(log))

    # Otros tipos de login
    elif path.startswith('/api-auth'):
        # Crear el log
        log = Logs_ConexionesUsuarios(
            direccion_ip=request.META.get('REMOTE_ADDR'),
            username=request.POST.get('username'),
            tipo_login=Logs_ConexionesUsuarios.TIPO_LOGIN_ENUM.OTRO,
        )

        if log.username is not None:
            log.save()  # Guardar el log en la BBDD
            yellow("LoggingMiddleware", str(log))
        else:
            error("(logging auth) NO USERNAME: %s" % request.user)


def _extract_user(request):
    """
    Intenta extraer, a partir del campo "user_id" del token de autorización, el usuario
    de la BBDD y lo guardamos internamente en la petición para propositos de logging.

    Devuelve True o False dependiendo de si el token era válido o no.
    """
    try:
        if request.user.pk is None:
            # Si falla esta linea, es que el middleware de autenticación ya se ejecutó y no es necesario
            jwt_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            # Descifrar el token y sacar el ID de usuario
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            # Guardar el usuario si lo hemos conseguido extraer
            request.user = User.objects.get(id=user_id)

        return True
    except (InvalidTokenError, IndexError):
        return False
