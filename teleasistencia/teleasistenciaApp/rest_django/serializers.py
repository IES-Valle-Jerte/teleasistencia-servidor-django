from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers

#Modelos propios:
from rest_framework.utils.representation import serializer_repr

from ..models import *

class ImagenUserSerializer(serializers.ModelSerializer):
   class Meta:
       model = Imagen_User
       fields = ['imagen']

class UserSerializer(serializers.ModelSerializer):

   imagen = ImagenUserSerializer(source='imagen_user', read_only=True)
   class Meta:
       model = User
       fields = ['id', 'url', 'last_login', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'groups', 'imagen']
       depth = 1

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['pk', 'name']

class Clasificacion_Recurso_Comunitario_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Clasificacion_Recurso_Comunitario
        fields = '__all__' #Indica todos los campos


class Tipo_Recurso_Comunitario_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Recurso_Comunitario
        fields = '__all__' #Indica todos los campos


class Recurso_Comunitario_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso_Comunitario
        fields = '__all__' #Indica todos los campos
        depth = 1

class Tipo_Alarma_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Alarma
        fields = '__all__' #Indica todos los campos
        depth = 1


class Clasificacion_Alarma_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Clasificacion_Alarma
        fields = '__all__' #Indica todos los campos


class Direccion_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__' #Indica todos los campos


class Persona_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__' #Indica todos los campos
        depth = 1


class Historico_Agenda_Llamadas_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Historico_Agenda_Llamadas
        fields = '__all__'
        depth = 2


class Agenda_Serializer(serializers.ModelSerializer):
    historico_agenda = Historico_Agenda_Llamadas_Serializer(
        many=True,
        read_only=True)
    class Meta:
        model = Agenda
        fields = '__all__' #Indica todos los campos
        depth = 2


class Tipo_Agenda_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Agenda
        fields = '__all__'


class Relacion_Terminal_Recurso_Comunitario_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Relacion_Terminal_Recurso_Comunitario
        fields = '__all__'
        depth = 3


class Terminal_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'
        depth = 2


class Historico_Tipo_Situación_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Historico_Tipo_Situacion
        fields = '__all__'
        depth = 1


class Tipo_Situacion_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Situacion
        fields = '__all__'


class Tipo_Vivienda_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Vivienda
        fields = '__all__'


class Relacion_Paciente_Persona_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Relacion_Paciente_Persona
        fields = '__all__'


class Paciente_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
        depth = 3


class Tipo_Modalidad_Paciente_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Modalidad_Paciente
        fields = '__all__'


class Recursos_Comunitarios_En_Alarma_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Recursos_Comunitarios_En_Alarma
        fields = '__all__'
        depth = 1


class Alarma_Serializer(serializers.ModelSerializer):
    # fecha_registro = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S%z"])
    class Meta:
        model = Alarma
        fields = '__all__'
        depth = 3
        
class Alarma_Programada_Serializer(serializers.ModelSerializer):
    # fecha_registro = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S%z"])
    class Meta:
        model = Alarma_Programada
        fields = '__all__'
        depth = 3

class Dispositivos_Auxiliares_en_Terminal_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivos_Auxiliares_En_Terminal
        fields = '__all__'
        depth = 1


class Persona_Contacto_En_Alarma_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Persona_Contacto_En_Alarma
        fields = '__all__'
        depth = 2


class Tecnologia_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnologia
        fields = '__all__' #Indica todos los campos
        depth = 2

class Desarrollador_Tecnologia_Serializer(serializers.ModelSerializer):

    # Devuelve también los datos de los datos de las tecnologias del Desarrollador_tecnologia
    tecnologias = Tecnologia_Serializer(
        many=True,
        read_only=True)

    class Meta:
        model = Desarrollador_Tecnologia
        fields = '__all__' #Indica todos los campos
        depth = 1

class Gestion_Base_Datos_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gestion_Base_Datos
        fields = '__all__'
        depth = 1


class Desarrollador_Serializer(serializers.ModelSerializer):

    # Devuelve también los datos de los datos de desarrolladores_tecnologias del Desarrollador
    desarrollador_tecnologias = Desarrollador_Tecnologia_Serializer(
        many=True,
        read_only=True)

    class Meta:
        model = Desarrollador
        fields = '__all__' #Indica todos los campos
        depth = 1

class Convocatoria_Proyecto_Serializer(serializers.ModelSerializer):

    # Devuelve también los datos de los desarrolladores de la convocatoria
    desarrolladores = Desarrollador_Serializer(
        many=True,
        read_only=True)

    class Meta:
        model = Convocatoria_Proyecto
        fields = '__all__' #Indica todos los campos
        depth = 1
