"""teleasistencia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static

#Django-Rest:
from rest_framework import routers
from teleasistenciaApp.rest_django import views_rest

# Para recuperación de contraseñas
from .views import get_csrf_token, TokenObtainPairSerializerWithLastLogin

#Autenticación rest con JWT:
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

#Para redirecciones simples con url:
from django.views.generic.base import RedirectView
from django.urls import re_path

#Router para la API REST
# Con trailing_slash=False hacemos que no intermprete la / final de la url, con esto podemos hacer GET, POST y DELETE
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', views_rest.UserViewSet)
router.register(r'groups', views_rest.GroupViewSet)
router.register(r'permission', views_rest.PermissionViewSet)
router.register(r'databases', views_rest.DatabaseViewSet)
router.register(r'clasificacion_recurso_comunitario', views_rest.Clasificacion_Recurso_Comunitario_ViewSet)
router.register(r'tipo_recurso_comunitario', views_rest.Tipo_Recurso_Comunitario_ViewSet)
router.register(r'recurso_comunitario', views_rest.Recurso_Comunitario_ViewSet)
router.register(r'tipo_alarma', views_rest.Tipo_Alarma_ViewSet)
router.register(r'clasificacion_alarma', views_rest.Clasificacion_Alarma_ViewSet)
router.register(r'direccion', views_rest.Direccion_ViewSet)
router.register(r'persona', views_rest.Persona_ViewSet)
router.register(r'agenda', views_rest.Agenda_ViewSet)
router.register(r'tipo_agenda', views_rest.Tipo_Agenda_ViewSet)
router.register(r'historico_agenda_llamadas', views_rest.Historico_Agenda_Llamadas_ViewSet)
router.register(r'relacion_terminal_recurso_comunitario', views_rest.Relacion_Terminal_Recurso_Comunitario_ViewSet)
router.register(r'terminal', views_rest.Terminal_ViewSet)
router.register(r'tipo_situacion', views_rest.Tipo_Situacion_ViewSet)
router.register(r'tipo_vivienda', views_rest.Tipo_Vivienda_ViewSet)
router.register(r'relacion_paciente_persona', views_rest.Relacion_Paciente_Persona_ViewSet)
router.register(r'paciente', views_rest.Paciente_ViewSet)
router.register(r'tipo_modalidad_paciente', views_rest.Tipo_Modalidad_Paciente_ViewSet)
router.register(r'recursos_comunitarios_en_alarma', views_rest.Recursos_Comunitarios_En_Alarma_ViewSet)
router.register(r'alarma', views_rest.Alarma_ViewSet)
router.register(r'cancelar_alarma', views_rest.Alarma_Cancelar_ViewSet)
router.register(r'alarma_programada', views_rest.Alarma_Programada_ViewSet)
router.register(r'dispositivos_auxiliares_en_terminal', views_rest.Dispositivos_Auxiliares_en_Terminal_ViewSet)
router.register(r'persona_contacto_en_alarma', views_rest.Persona_Contacto_En_Alarma_ViewSet)
router.register(r'gestion_base_datos', views_rest.Gestion_Base_Datos_ViewSet)
router.register(r'profile', views_rest.ProfileViewSet)
router.register(r'desarrollador_tecnologia', views_rest.DesarrolladorTecnologiaViewSet)
router.register(r'seguimiento_teleoperador', views_rest.SeguimientoTeleoperador)


urlpatterns = [
#path('admin/', admin.site.urls),
    re_path(r'^$', RedirectView.as_view(url='/teleasistencia', permanent=False), name='index'),
    url(r'^teleasistencia/', include('teleasistenciaApp.urls')),
    url(r'^admin/', admin.site.urls, name='admin'),
    #URLS de login y logout de django.contrib.auth:
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    #Django Api Rest Framework
    path('api-rest/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #Django Rest social Auth:
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    #Django Rest Simple JWT:
    path('api/token/', TokenObtainPairView.as_view(serializer_class=TokenObtainPairSerializerWithLastLogin), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # URLs de recuperación de contraseñas de usuarios de Django (desde navegador)
    path('api-rest/password_reset/csrf', get_csrf_token, name='password_reset_csrf'),
    # [password_reset_form.html] Aqui se hace la petición, enviando el correo que algún usuario (User) + token csrf)
    path('api-rest/password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    # [password_reset_done.html] Después del post, te redirige aquí para que sepas que la petición se ha gestionado
    path('api-rest/password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # [password_reset_confirm.html] A donde te manda el link recibido por correo
    path('api-rest/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # [password_reset_complete.html] Ventana de confirmación de cambio de contraseña
    path('api-rest/reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
# añadimos el media url y el media root para poder visualizar las imagenes de usuario
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

