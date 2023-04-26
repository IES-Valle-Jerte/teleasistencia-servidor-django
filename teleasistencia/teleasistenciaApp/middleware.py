import jwt
from jwt.exceptions import InvalidTokenError

from django.conf import settings
from django.contrib.auth.models import User

import json
from urllib.parse import parse_qs

from .models import Logs_AccionesUsuarios, Logs_ConexionesUsuarios
from utilidad.logging import info, error, yellow

class LoggingMiddleware:
    """
    Middleware encargado de loggear
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Guardar el body porque no puede ser accedido después de procesar la petición
        req_body = request.body
        # Procesar la petición y loggear (si es necesario)
        response = self.get_response(request)
        log_request(request, req_body, response)

        # En caso de no estar autorizado, el SecurityMiddleware habrá dado una respuesta adecuada
        return response


def log_request(request, req_body, response):
    # ##############  Ignorados ############## #
    if request.path.startswith(('api-rest/password_reset/', 'api-rest/reset/')):
        pass
    # ################ Logins ################ #
    elif request.path.startswith(('/api/token', '/admin/login', '/api-auth')):
        _log_loging_request(request, req_body, response)
    # ############### Acciones ############### #
    else:
        _extract_user(request)
        _log_action_request(request, response)


def _log_action_request(request, response):
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


def _log_loging_request(request, req_body, response):
    path = request.path
    req_body = req_body.decode().strip()

    # Crear el log
    log = Logs_ConexionesUsuarios(
        direccion_ip=request.META.get('REMOTE_ADDR'),
    )

    # ################ Logins ################ #
    # Logins de la api-rest para obtener Token JWT
    if path.startswith('/api/token'):
        log.tipo_login = Logs_ConexionesUsuarios.TIPO_LOGIN_ENUM.TOKEN_API
        log.login_correcto = (response.status_code == 200)

        # Postman y Angular envia los datos como JSON, android como URLencoded
        # Intentar parsear a los distintos tipos de dato
        try:
            req_body = json.loads(req_body)
            log.username = req_body.get('username')
        except ValueError:
            req_body = parse_qs(req_body)
            log.username = req_body.get('username', [None])[0]

        log.save()  # Guardar el log en la BBDD
        yellow("LoggingMiddleware", str(log))

        # Logins por panel de administración (las acciones se quedan registradas en otro lado)
    elif path.startswith('/admin/login') and request.method == "POST":
        log.username = request.POST.get('username')
        log.tipo_login = Logs_ConexionesUsuarios.TIPO_LOGIN_ENUM.PANEL_ADMIN
        log.login_correcto = (response.status_code == 302)

        log.save()  # Guardar el log en la BBDD
        yellow("LoggingMiddleware", str(log))

    # Otros tipos de login
    # elif path.startswith('/api-auth'):
    #     pass


def _extract_user(request):
    """
    Intenta extraer, a partir del campo "user_id" del token de autorización, el usuario
    de la BBDD y lo guardamos internamente en la petición para propositos de logging.

    Devuelve True o False dependiendo de si el token era válido o no.
    """
    try:
        if not request.user.is_anonymous and request.user.pk is None:
            # Si falla esta linea, es que el middleware de autenticación ya se ejecutó y no es necesario
            jwt_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            # Guardar el usuario si lo hemos conseguido extraer
            request.user = User.objects.get(id=user_id)
            return True
        else:
            return False
    except (InvalidTokenError, IndexError):
        return False
