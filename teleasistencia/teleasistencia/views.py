from django.middleware.csrf import get_token
from django.http import JsonResponse

from django.utils.timezone import now
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def get_csrf_token(request):
    # Obtener tokens CSRF para recuperación de contraseña
    token = get_token(request)
    return JsonResponse({'csrf_token': token})


class TokenObtainPairSerializerWithLastLogin(TokenObtainPairSerializer):
    """
    TokenObtainPairSerializar customizado para que se guarde la fecha de último login
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Actualizar timestamp last login
        user.last_login = now()
        user.save()

        return data
