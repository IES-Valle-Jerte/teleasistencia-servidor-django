from django.middleware.csrf import get_token
from django.http import JsonResponse


def get_csrf_token(request):
    # Obtener tokens CSRF para recuperación de contraseña
    token = get_token(request)
    return JsonResponse({'csrf_token': token})
