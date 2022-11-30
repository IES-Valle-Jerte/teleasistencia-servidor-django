from http.client import HTTPResponse
from pathlib import Path
import os

from django.shortcuts import _get_queryset
from requests import request

from django.contrib.auth.models import User, Group, Permission

import os
import shutil
# Imports necesarios para la gestion de la base de datos
from datetime import datetime

from django.contrib.auth.models import User, Group, Permission
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
# Serializadores generales
from rest_framework.response import Response

from .utils import getQueryAnd
# Modelos propios
from ..models import *
# Serializadores propios
from ..rest_django.serializers import *
from django.http import JsonResponse

# Alarmas
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Comprobamos si el usuario es profesor. Se utiliza para la discernir entre solicitudes de Profesor y Teleoperador
class IsTeacherMember(permissions.BasePermission):

    def has_permission(self, request, view):
        #return True
        if request.user.groups.filter(name="profesor").exists():
            return True

# Creamos la vista Recurso Comunitario Personal de tipo viewSet que retorna un JSON
class Recurso_comunitario_personalViewSet(viewsets.ViewSet):
    def list(self,request, *args, **kwargs):
        data=[

        ]
        #Obtenemos los pacientes y los tipos de centro sanitario y de recurso comuniatario
        pacientes = Paciente.objects.all().order_by('id_persona')
        tipos_centro_santario = Tipo_Centro_Sanitario.objects.all().order_by('nombre')
        tipos_recurso_comunitario=Tipo_Recurso_Comunitario.objects.all().order_by('nombre')
        #Recorremos los pacientes y obetensmos loas datos que deseesmos
        for paciente in pacientes:
            dataPaciente={
                "id_paciente": paciente.id,
                "Nombre": paciente.id_persona.nombre,
                "Apellidos": paciente.id_persona.apellidos,
                "Sexo":paciente.id_persona.sexo,
                "Localidad":paciente.id_persona.id_direccion.localidad,
                "Direccion":paciente.id_persona.id_direccion.direccion,
                "Provincia": paciente.id_persona.id_direccion.provincia,
            }
                #recorro los tipo de centro sanitario
            for tipo_centro_santario in tipos_centro_santario:
                #obtengo los centros segun el id de tipos centro sanitario
                centro_sanitario = Centro_Sanitario.objects.filter(id_tipos_centro_sanitario=tipo_centro_santario)
                #si el array es nulo
                if not centro_sanitario:
                    dataPaciente[tipo_centro_santario.nombre]=""
                    #sino
                else:
                    # obtengo la relacion usuario centro segun el id de centro y el id de paciente
                    relaciones_usuario_centro = Relacion_Usuario_Centro.objects.filter(id_paciente=paciente.id).filter(id_centro_sanitario__in=centro_sanitario).first()
                    if relaciones_usuario_centro is not None:
                        #si no es null muestro elnombre del centro sanitario

                        dataPaciente[tipo_centro_santario.nombre] = relaciones_usuario_centro.id_centro_sanitario.nombre

                    else:
                            dataPaciente[tipo_centro_santario.nombre]=""
            # recorro los tipo de recurso comunitario
            for tipo_recurso_comunitario in tipos_recurso_comunitario:
                # obtengo los recursos segun el id de tipos recursos comunitarios
                recurso_comunitario=Recurso_Comunitario.objects.filter(id_tipos_recurso_comunitario=tipo_recurso_comunitario)
                # si el array es nulo comillas vacías
                if not recurso_comunitario:
                    dataPaciente[tipo_recurso_comunitario.nombre] = ""
                else:
                    # obtengo la relacion terminal recurso segun el id de terminal y el id del recurso comunitario
                    relacion_terminal_recurso_comunitario= Relacion_Terminal_Recurso_Comunitario.objects.filter(id_terminal=paciente.id_terminal).filter(id_recurso_comunitario__in=recurso_comunitario).first()
                    if relacion_terminal_recurso_comunitario is not None:
                        dataPaciente[tipo_recurso_comunitario.nombre] =relacion_terminal_recurso_comunitario.id_recurso_comunitario.nombre
                    else:
                        # sino tienen nada comillas vacías
                        dataPaciente[tipo_recurso_comunitario.nombre] = ""
            #Incluimos los datos en el Array principal y lo retornamos
            data.append(dataPaciente)
        return JsonResponse(data,safe=False)

# Creamos la vista Profile que  modificara los datos y retornara la informacion del usuario activo en la aplicación
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    def list(self, request, *args, **kwargs):
        #Obtenemos el usuario filtrando por el usuario de la request
        queryset = User.objects.filter(username=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        if request.data.get("email") is not None:
            user.email = request.data.get("email")
        if request.data.get("password") is not None:
            # Encriptamos la contraseña
            user.set_password(request.data.get("password"))
        user.save()
        # si se modifican Files es decir la imagen
        if request.FILES:
            #obtengo la imagem eue me modifican
            img = request.FILES["imagen"]
            image = Imagen_User.objects.filter(user=user).first()
            #Si ya tenia imagen borro la anterior y la guardo add al usuario
            if image:
                if (image.imagen) is not None:
                    os.remove(image.imagen.path)
                image.imagen = img
                image.save()
            #Si no tenia imagen se la añado al usuario
            else:
                image = Imagen_User(
                    user=user,
                    imagen=img
                )
            image.save()

        # Devolvemos el user modificado con su imagen
        user_serializer = self.get_serializer(user, many=False)
        return Response(user_serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser]

    # Obtenemos el listado de personas filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = User.objects.filter(query)
        # En el caso de que no hay parámetros y queramos devolver todos los valores
        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe el groups
        id_groups = Group.objects.get(pk=request.data.get("groups"))

        if id_groups is None:
            return Response("Error: Groups")

        if User.objects.filter(username=request.data.get("username")).exists():
            return Response("El usuario ya existe")


        user = User(
            username=request.data.get("username"),
            first_name=request.data.get("first_name"),
            last_name=request.data.get("last_name"),
            email=request.data.get("email"),
        )


        # Encriptamos la contraseña
        user.set_password(request.data.get("password"))
        user.save()
        user.groups.add(id_groups)

        if request.FILES:
            img = request.FILES["imagen"]
            image = Imagen_User(
                user=user,
                imagen=img
            )
            image.save()
        # Devolvemos el user creado
        user_serializer = self.get_serializer(user, many=False)
        return Response(user_serializer.data)

    def update(self, request, *args, **kwargs):
        # TODO comprobar si un usuario (no-profesor) puede modificar sus datos
        # Comprobamos que existe el groups
        id_groups = Group.objects.get(pk=request.data.get("groups"))
        if id_groups is None:
            return Response("Error: Groups")

        user = User.objects.get(pk=kwargs["pk"])
        user.groups.clear()
        user.groups.add(id_groups)
        if request.data.get("username") is not None:
            user.username = request.data.get("username")
        if request.data.get("email") is not None:
            user.email = request.data.get("email")
        if request.data.get("password") is not None:
            # Encriptamos la contraseña
            user.set_password(request.data.get("password"))
        user.save()
        if request.FILES:
            img = request.FILES["imagen"]
            image = Imagen_User.objects.filter(user=user).first()
            if image:
                if (image.imagen) is not None:
                    os.remove(image.imagen.path)
                image.imagen = img
                image.save()
            else:
                image = Imagen_User(
                    user=user,
                    imagen=img
                )
            image.save()

        # Devolvemos el user creado
        user_serializer = self.get_serializer(user, many=False)
        return Response(user_serializer.data)

    def destroy(self, request, *args, **kwargs):
        print(kwargs)
        user = User.objects.get(pk=kwargs["pk"])
        try:
          image = Imagen_User.objects.get(user=user)

          if image.imagen is not None:
             os.remove(image.imagen.path)
        except:
            print('error propio')
        user.delete()
        return Response('borrado')


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    # permission_classes = [permissions.IsAdminUser]
    permission_classes = [IsTeacherMember]


class Tipo_Recurso_Comunitario_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Recurso_Comunitario.objects.all()
    serializer_class = Tipo_Recurso_Comunitario_Serializer
    # Habría que descomentar la siguiente línea para permitir las acciones sólo a los usuarios autenticados (Authorization en la petición POST)
    # permission_classes = [permissions.IsAuthenticated] # Si quieriéramos para todos los registrados: IsAuthenticated]
    permission_classes = [IsTeacherMember]


class Recurso_Comunitario_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Recurso_Comunitario.objects.all()
    serializer_class = Recurso_Comunitario_Serializer

    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]

    def create(self, request, *args, **kwargs):

        # Comprobamos que el tipo de centro sanitario existe
        tipos_recurso_comunitario = Tipo_Recurso_Comunitario.objects.get(
            pk=request.data.get("id_tipos_recurso_comunitario"))
        if tipos_recurso_comunitario is None:
            return Response("Error: tipos_recurso_comunitario")

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion = direccion_serializer.save()
        else:
            return Response("Error: direccion")

        # Creamos el centro sanitario con el tipo de centro y la dirección
        recurso_comunitario = Recurso_Comunitario(
            nombre=request.data.get("nombre"),
            telefono=request.data.get("telefono"),
            id_tipos_recurso_comunitario=tipos_recurso_comunitario,
            id_direccion=direccion
        )
        recurso_comunitario.save()

        # Devolvemos los datos
        recurso_comunitario_serializer = Recurso_Comunitario_Serializer(recurso_comunitario)
        return Response(recurso_comunitario_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que el tipo de centro sanitario existe
        tipos_recurso_comunitario = Tipo_Recurso_Comunitario.objects.get \
            (pk=request.data.get("id_tipos_recurso_comunitario"))
        if tipos_recurso_comunitario is None:
            return Response("Error: tipos_recurso_comunitario")

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion = direccion_serializer.save()
        else:
            return Response("Error: direccion")

        # Modificamos el centro sanitario con el tipo de centro y la dirección
        recurso_comunitario = Recurso_Comunitario.objects.get(pk=kwargs["pk"])
        recurso_comunitario.nombre = request.data.get("nombre")
        recurso_comunitario.telefono = request.data.get("telefono")
        recurso_comunitario.id_tipos_recurso_comunitario = tipos_recurso_comunitario
        recurso_comunitario.id_direccion = direccion

        recurso_comunitario.save()
        # Devolvemos los datos
        recurso_comunitario_serializer = Recurso_Comunitario_Serializer(recurso_comunitario)
        return Response(recurso_comunitario_serializer.data)



class Centro_Sanitario_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Centro_Sanitario.objects.all()
    serializer_class = Centro_Sanitario_Serializer

    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]

    def create(self, request, *args, **kwargs):

        # Comprobamos que el tipo de centro sanitario existe
        tipo_centro_sanitario = Tipo_Centro_Sanitario.objects.get(pk=request.data.get("id_tipos_centro_sanitario"))
        if tipo_centro_sanitario is None:
            return Response("Error: tipo_centro_sanitario")

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion = direccion_serializer.save()
        else:
            return Response("Error: direccion")

        # Creamos el centro sanitario con el tipo de centro y la dirección
        centro_sanitario = Centro_Sanitario(
            nombre=request.data.get("nombre"),
            telefono=request.data.get("telefono"),
            id_tipos_centro_sanitario=tipo_centro_sanitario,
            id_direccion=direccion
        )
        centro_sanitario.save()

        # Devolvemos los datos
        centro_sanitario_serializer = Centro_Sanitario_Serializer(centro_sanitario)
        return Response(centro_sanitario_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que el tipo de centro sanitario existe
        tipo_centro_sanitario = Tipo_Centro_Sanitario.objects.get(pk=request.data.get("id_tipos_centro_sanitario"))
        if tipo_centro_sanitario is None:
            return Response("Error: tipo_centro_sanitario")

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion = direccion_serializer.save()
        else:
            return Response("Error: direccion")

        centro_sanitario = Centro_Sanitario.objects.get(pk=kwargs["pk"])
        centro_sanitario.id_tipos_centro_sanitario = tipo_centro_sanitario
        centro_sanitario.nombre = request.data.get("nombre")
        centro_sanitario.telefono = request.data.get("telefono")
        centro_sanitario.id_direccion = direccion

        centro_sanitario.save()

        # Devolvemos los datos
        centro_sanitario_serializer = Centro_Sanitario_Serializer(centro_sanitario)
        return Response(centro_sanitario_serializer.data)


class Tipo_Centro_Sanitario_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Centro_Sanitario.objects.all()
    serializer_class = Tipo_Centro_Sanitario_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]
    permission_classes = [IsTeacherMember]


class Tipo_Alarma_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Alarma.objects.all()
    serializer_class = Tipo_Alarma_Serializer
    permission_classes = [IsTeacherMember]

    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Comprobamos que el tipo de centro sanitario existe
        clasificacion_alarma = Clasificacion_Alarma.objects.get(pk=request.data.get("id_clasificacion_alarma"))
        if clasificacion_alarma is None:
            return Response("Error: id_clasificacion_alarma")

        # Creamos el tipo_alarma
        tipo_alarma = Tipo_Alarma(
            nombre=request.data.get("nombre"),
            codigo=request.data.get("codigo"),
            es_dispositivo=request.data.get("es_dispositivo"),
            id_clasificacion_alarma=clasificacion_alarma
        )
        tipo_alarma.save()

        # Devolvemos el tipo de alarma creado
        tipo_alarma_serializer = Tipo_Alarma_Serializer(tipo_alarma)
        return Response(tipo_alarma_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que el tipo de centro sanitario existe
        clasificacion_alarma = Clasificacion_Alarma.objects.get(pk=request.data.get("id_clasificacion_alarma"))
        if clasificacion_alarma is None:
            return Response("Error: id_clasificacion_alarma")

        # Modificamos el tipo_alarma
        tipo_alarma = Tipo_Alarma.objects.get(pk=kwargs["pk"])
        if request.data.get("nombre") is not None:
            tipo_alarma.nombre = request.data.get("nombre")
        if request.data.get("codigo") is not None:
            tipo_alarma.codigo = request.data.get("codigo")
        if request.data.get("es_dispositivo") is not None:
            tipo_alarma.es_dispositivo = request.data.get("es_dispositivo")
        tipo_alarma.id_clasificacion_alarma = clasificacion_alarma

        tipo_alarma.save()
        # Devolvemos el tipo de alarma modificado
        tipo_alarma_serializer = Tipo_Alarma_Serializer(tipo_alarma)
        return Response(tipo_alarma_serializer.data)



class Clasificacion_Alarma_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Clasificacion_Alarma.objects.all()
    serializer_class = Clasificacion_Alarma_Serializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]


class Direccion_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Direccion.objects.all()
    serializer_class = Direccion_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]




def Asignar_Persona_Direccion(data, direccion):
    persona = Persona(
        nombre=data.get("nombre"),
        apellidos=data.get("apellidos"),
        dni=data.get("dni"),
        fecha_nacimiento=data.get("fecha_nacimiento"),
        sexo=data.get("sexo"),
        telefono_fijo=data.get("telefono_fijo"),
        telefono_movil=data.get("telefono_movil"),
        id_direccion=direccion
    )
    persona.save()

    return persona

# TODO echar un vistazo a los metodos detallamente  y a la tabla postman (puede que no esten bien definidos)
class Persona_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Persona.objects.all()
    serializer_class = Persona_Serializer

    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de personas filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Persona.objects.filter(query)
        # En el caso de que no hay parámetros y queramos devolver todos los valores
        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Creamos una persona con por POST
    def create(self, request, *args, **kwargs):

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion = direccion_serializer.save()
        else:
            return Response("Error: direccion")

        # Creamos la persona con la dirección y la devolvemos
        persona_serializer = Persona_Serializer(Asignar_Persona_Direccion(request.data, direccion))
        return Response(persona_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos si los datos se introducen para una dirección ya existente,
        id_direccion = request.data.get("id_direccion")

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion = direccion_serializer.save()
        else:
            return Response("Error: direccion")

        persona = Persona.objects.get(pk=kwargs["pk"])
        if request.data.get("nombre") is not None:
            persona.nombre = request.data.get("nombre")
        if request.data.get("apellidos") is not None:
            persona.apellidos = request.data.get("apellidos")
        if request.data.get("dni") is not None:
            persona.dni = request.data.get("dni")
        if request.data.get("fecha_nacimiento") is not None:
            persona.fecha_nacimiento = request.data.get("fecha_nacimiento")
        if request.data.get("sexo") is not None:
            persona.sexo = request.data.get("sexo")
        if request.data.get("telefono_fijo") is not None:
            persona.telefono_fijo = request.data.get("telefono_fijo")
        if request.data.get("telefono_movil") is not None:
            persona.telefono_movil = request.data.get("telefono_movil")
        #persona.id_direccion = direccion

        # Obtenemos los datos de dirección y los almacenamos
        direccion_serializer = Direccion_Serializer(data=request.data.get("id_direccion"))
        if direccion_serializer.is_valid():
            direccion_serializer.id = persona.id_direccion
            direccion_serializer.save()
        else:
            return Response("Error: direccion")

        persona.save()
        persona_serializer = Persona_Serializer(persona)
        return Response(persona_serializer.data)


class Agenda_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Agenda.objects.all()
    serializer_class = Agenda_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de la Agenda filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

    # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Agenda.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe id_paciente
        id_paciente = Paciente.objects.get(pk=request.data.get("id_paciente"))
        if id_paciente is None:
            return Response("Error: id_paciente")

        # Comprobamos que existe id_tipo_agenda
        id_tipo_agenda = Tipo_Agenda.objects.get(pk=request.data.get("id_tipo_agenda"))
        if id_tipo_agenda is None:
            return Response("Error: id_tipo_agenda")

        # Comprobamos que existe id_persona
        id_persona = Persona.objects.get(pk=request.data.get("id_persona"))
        if id_persona is None:
            return Response("Error: id_persona")

        agenda = Agenda(
            id_persona=id_persona,
            id_tipo_agenda=id_tipo_agenda,
            id_paciente=id_paciente,
            fecha_registro=request.data.get("fecha_registro"),
            fecha_prevista=request.data.get("fecha_prevista"),
            fecha_resolucion=request.data.get("fecha_resolucion"),
            observaciones=request.data.get("observaciones")
        )
        agenda.save()

        # Devolvemos la agenda creada
        agenda_serializer = Agenda_Serializer(agenda)
        return Response(agenda_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe id_paciente
        id_paciente = Paciente.objects.get(pk=request.data.get("id_paciente"))
        if id_paciente is None:
            return Response("Error: id_paciente")

        # Comprobamos que existe id_tipo_agenda
        id_tipo_agenda = Tipo_Agenda.objects.get(pk=request.data.get("id_tipo_agenda"))
        if id_tipo_agenda is None:
            return Response("Error: id_tipo_agenda")

        # Comprobamos que existe id_persona
        id_persona = Persona.objects.get(pk=request.data.get("id_persona"))
        if id_persona is None:
            return Response("Error: id_persona")

        agenda = Agenda.objects.get(pk=kwargs["pk"])
        agenda.id_tipo_agenda = id_tipo_agenda
        agenda.id_persona = id_persona
        agenda.id_paciente = id_paciente
        if request.data.get("fecha_registro") is not None:
            agenda.fecha_registro = request.data.get("fecha_registro")
        if request.data.get("fecha_prevista") is not None:
            agenda.fecha_prevista = request.data.get("fecha_prevista")
        if request.data.get("fecha_resolucion") is not None:
            agenda.fecha_resolucion = request.data.get("fecha_resolucion")
        if request.data.get("observaciones") is not None:
            agenda.observaciones = request.data.get("observaciones")

        agenda.save()

        # Devolvemos la agenda modificada
        agenda_serializer = Agenda_Serializer(agenda)
        return Response(agenda_serializer.data)


class Tipo_Agenda_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Agenda.objects.all()
    serializer_class = Tipo_Agenda_Serializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser] # Si quieriéramos para todos los registrados: IsAuthenticated]


class Historico_Agenda_Llamadas_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Historico_Agenda_Llamadas.objects.all()
    serializer_class = Historico_Agenda_Llamadas_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de el Hiscorico_Agenda_Llamadas filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Historico_Agenda_Llamadas.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe la agenda
        id_agenda = Agenda.objects.get(pk=request.data.get("id_agenda"))
        if id_agenda is None:
            return Response("Error: id_agenda")

        # Comprobamos que existe el id del operador en la tabla user
        id_teleoperador = User.objects.get(pk=request.data.get("id_teleoperador"))
        if id_teleoperador is None:
            return Response("Error: id_teleoperador")

        historico_agenda_llamada = Historico_Agenda_Llamadas(
            id_agenda=id_agenda,
            id_teleoperador=id_teleoperador,
            fecha_llamada=request.data.get("fecha_llamada"),
            observaciones=request.data.get("observaciones")
        )
        historico_agenda_llamada.save()

        # Devolvemos el historico_agenda_llamada
        historico_agenda_llamada_serializer = Historico_Agenda_Llamadas_Serializer(historico_agenda_llamada)
        return Response(historico_agenda_llamada_serializer.data)


class Relacion_Terminal_Recurso_Comunitario_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Relacion_Terminal_Recurso_Comunitario.objects.all()
    serializer_class = Relacion_Terminal_Recurso_Comunitario_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de relacion_terminal_recurso_comunitario filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Relacion_Terminal_Recurso_Comunitario.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que exite el terminal
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Comprobamos que existe el recurso comunitario
        id_recurso_comunitario = Recurso_Comunitario.objects.get(pk=request.data.get("id_recurso_comunitario"))
        if id_recurso_comunitario is None:
            return Response("Error: id_recurso_comunitario")

        relacion_terminal_recurso_comunitario = Relacion_Terminal_Recurso_Comunitario(
            id_terminal=id_terminal,
            id_recurso_comunitario=id_recurso_comunitario
        )

        relacion_terminal_recurso_comunitario.save()

        # Devolvemos la relacion_terminal_recurso_comunitario
        relacion_terminal_recurso_comunitario_serializer = Relacion_Terminal_Recurso_Comunitario_Serializer \
            (relacion_terminal_recurso_comunitario)
        return Response(relacion_terminal_recurso_comunitario_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que exite el terminal
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Comprobamos que existe el recurso comunitario
        id_recurso_comunitario = Recurso_Comunitario.objects.get(pk=request.data.get("id_recurso_comunitario"))
        if id_recurso_comunitario is None:
            return Response("Error: id_recurso_comunitario")

        relacion_terminal_recurso_comunitario = Relacion_Terminal_Recurso_Comunitario.objects.get(pk=kwargs["pk"])
        relacion_terminal_recurso_comunitario.id_terminal = id_terminal
        relacion_terminal_recurso_comunitario.id_recurso_comunitario = id_recurso_comunitario

        relacion_terminal_recurso_comunitario.save()

        relacion_terminal_recurso_comunitario_serializer = Relacion_Terminal_Recurso_Comunitario_Serializer(
            relacion_terminal_recurso_comunitario)
        return Response(relacion_terminal_recurso_comunitario_serializer.data)



class Terminal_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Terminal.objects.all()
    serializer_class = Terminal_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            try:
                queryset = Terminal.objects.filter(query)
            except:
                try:
                    id_persona = Persona.objects.get(query)
                    id_paciente = Paciente.objects.get(id_persona=id_persona)
                    queryset = Terminal.objects.filter(id_titular=id_paciente)
                except:
                    return Response("No hay terminal asociado")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe id_tipo_vivienda
        id_tipo_vivienda = Tipo_Vivienda.objects.get(pk=request.data.get("id_tipo_vivienda"))
        if id_tipo_vivienda is None:
            return Response("Error: id_tipo_vivienda")

        # Comprobamos que existe el id_titular
        id_titular = Paciente.objects.get(pk=request.data.get("id_titular"))
        if id_titular is None:
            return Response("Error: id_titular")

        terminal = Terminal(
            numero_terminal=request.data.get("numero_terminal"),
            modo_acceso_vivienda=request.data.get("modo_acceso_vivienda"),
            barreras_arquitectonicas=request.data.get("barreras_arquitectonicas"),
            id_tipo_vivienda=id_tipo_vivienda,
            id_titular=id_titular
        )
        terminal.save()

        # Devolvemos el terminal creado
        terminal_serializer = Terminal_Serializer(terminal)
        return Response(terminal_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe id_tipo_vivienda
        id_tipo_vivienda = Tipo_Vivienda.objects.get(pk=request.data.get("id_tipo_vivienda"))
        if id_tipo_vivienda is None:
            return Response("Error: id_tipo_vivienda")

        # Comprobamos que existe el id_titular
        id_titular = Paciente.objects.get(pk=request.data.get("id_titular"))
        if id_titular is None:
            return Response("Error: id_titular")

        terminal = Terminal.objects.get(pk=kwargs["pk"])
        terminal.id_tipo_vivienda = id_tipo_vivienda
        terminal.id_titular = id_titular
        if request.data.get("numero_terminal") is not None:
            terminal.numero_terminal = request.data.get("numero_terminal")
        if request.data.get("modo_acceso_vivienda") is not None:
            terminal.modo_acceso_vivienda = request.data.get("modo_acceso_vivienda")
        if request.data.get("barreras_arquitectonicas") is not None:
            terminal.barreras_arquitectonicas = request.data.get("barreras_arquitectonicas")

        terminal.save()

        # Devolvemos el terminal modificado
        terminal_serializer = Terminal_Serializer(terminal)
        return Response(terminal_serializer.data)


class Historico_Tipo_Situacion_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Historico_Tipo_Situacion.objects.all()
    serializer_class = Historico_Tipo_Situación_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Comprobamos que el tipo situacion existe
        id_tipo_situacion = Tipo_Situacion.objects.get(pk=request.data.get("id_tipo_situacion"))
        if id_tipo_situacion is None:
            return Response("Error: id_tipo_situacion")

        # Comprobamos que el terminal existe
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Creamos el historico_tipo_situacion
        historico_tipo_situacion = Historico_Tipo_Situacion(
            fecha=request.data.get("fecha"),
            id_tipo_situacion=id_tipo_situacion,
            id_terminal=id_terminal
        )

        historico_tipo_situacion.save()
        # Devolvemos el historico_tipo_situación creado
        historico_tipo_situacion_serializer = Historico_Tipo_Situación_Serializer(historico_tipo_situacion)
        return Response(historico_tipo_situacion_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que el tipo situacion existe
        id_tipo_situacion = Tipo_Situacion.objects.get(pk=request.data.get("id_tipo_situacion"))
        if id_tipo_situacion is None:
            return Response("Error: id_tipo_situacion")

        # Comprobamos que el terminal existe
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Modificamos el historico_tipo_situacion
        historico_tipo_situacion = Historico_Tipo_Situacion.objects.get(pk=kwargs["pk"])
        historico_tipo_situacion.id_tipo_situacion = id_tipo_situacion
        historico_tipo_situacion.id_terminal = id_terminal
        historico_tipo_situacion.fecha = request.data.get("fecha")

        historico_tipo_situacion.save()

        historico_tipo_situacion_serializer = Historico_Tipo_Situación_Serializer(historico_tipo_situacion)
        return Response(historico_tipo_situacion_serializer.data)



class Tipo_Situacion_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Situacion.objects.all()
    serializer_class = Tipo_Situacion_Serializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]


class Tipo_Vivienda_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Vivienda.objects.all()
    serializer_class = Tipo_Vivienda_Serializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]


class Relacion_Paciente_Persona_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Relacion_Paciente_Persona.objects.all()
    serializer_class = Relacion_Paciente_Persona_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de relacion_paciente_persona filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Relacion_Paciente_Persona.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe el paciente que recibimos como parametro get
        id_paciente = Paciente.objects.get(pk=request.data.get("id_paciente"))
        if id_paciente is None:
            return Response("Error: id_paciente")
        # Comprobamos que existe la persona
        id_persona = Persona.objects.get(pk=request.data.get("id_persona"))
        if id_persona is None:
            return Response("Error: id_persona")

        # Creamos la relacion_paciente_persona
        relacion_paciente_persona = Relacion_Paciente_Persona(
            id_paciente=id_paciente,
            id_persona=id_persona,
            tipo_relacion=request.data.get("tipo_relacion"),
            tiene_llaves_vivienda=request.data.get("tiene_llaves_vivienda"),
            disponibilidad=request.data.get("disponibilidad"),
            observaciones=request.data.get("observaciones"),
            prioridad=request.data.get("prioridad")
        )
        relacion_paciente_persona.save()

        # Devolvemos la relacion_paciente_persona creada
        relacion_paciente_persona_serilizer = Relacion_Paciente_Persona_Serializer(relacion_paciente_persona)
        return Response(relacion_paciente_persona_serilizer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe el paciente
        id_paciente = Paciente.objects.get(pk=request.data.get("id_paciente"))
        if id_paciente is None:
            return Response("Error: id_paciente")
        # Comprobamos que existe la persona
        id_persona = Persona.objects.get(pk=request.data.get("id_persona"))
        if id_persona is None:
            return Response("Error: id_persona")

        # Modificamos la relacion_paciente_persona
        relacion_paciente_persona = Relacion_Paciente_Persona.objects.get(pk=kwargs["pk"])
        if request.data.get("tipo_relacion") is not None:
            relacion_paciente_persona.tipo_relacion = request.data.get("tipo_relacion")
        if request.data.get("tiene_llaves_vivienda") is not None:
            relacion_paciente_persona.tiene_llaves_vivienda = request.data.get("tiene_llaves_vivienda")
        if request.data.get("disponibilidad") is not None:
            relacion_paciente_persona.disponibilidad = request.data.get("disponibilidad")
        if request.data.get("observaciones") is not None:
            relacion_paciente_persona.observaciones = request.data.get("observaciones")
        if request.data.get("prioridad") is not None:
            relacion_paciente_persona.prioridad = request.data.get("prioridad")
        relacion_paciente_persona.id_persona = id_persona
        relacion_paciente_persona.id_paciente = id_paciente

        relacion_paciente_persona.save()

        # Devolvemos la relacion_paciente_persona modificada
        relacion_paciente_persona_serilizer = Relacion_Paciente_Persona_Serializer(relacion_paciente_persona)
        return Response(relacion_paciente_persona_serilizer.data)


class Paciente_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Paciente.objects.all()
    serializer_class = Paciente_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de pacientes filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            try:
                queryset = Paciente.objects.filter(query)
            except:
                try:
                    id_persona = Persona.objects.get(query)
                    queryset = Paciente.objects.filter(id_persona=id_persona)
                except:
                    return Response("No existe el paciente")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Creamos el paciente
    def create(self, request, *args, **kwargs):
        # Comprobamos que existe el id_terminal
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Comprobamos que existe id_tipo_modalidad_paciente
        id_modalidad_paciente = Tipo_Modalidad_Paciente.objects.get(pk=request.data.get("id_tipo_modalidad_paciente"))
        if id_modalidad_paciente is None:
            return Response("Error: id_modalidad_paciente")

        # Comprobamos si los datos que recibimos de persona existen
        id_persona = request.data.get("id_persona")
        if id_persona is None:
            if request.data.get("persona") is not None:
                persona = Asignar_Persona_Direccion(data=request.data.get("persona"), direccion=Direccion.objects.get
                    (pk=request.data.get("persona")["id_direccion"]))
            else:
                return Response("Error: persona")
        else:
            persona = Persona.objects.get(pk=id_persona)

        paciente = Paciente(
            id_persona=persona,
            id_tipo_modalidad_paciente=id_modalidad_paciente,
            id_terminal=id_terminal,
            tiene_ucr=request.data.get("tiene_ucr"),
            numero_expediente=request.data.get("numero_expediente"),
            numero_seguridad_social=request.data.get("numero_seguridad_social"),
            prestacion_otros_servicios_sociales=request.data.get("prestacion_otros_servicios_sociales"),
            observaciones_medicas=request.data.get("observaciones_medicas"),
            intereses_y_actividades=request.data.get("intereses_y_actividades")
        )
        paciente.save()

        # Devolvemos el paciente creado
        paciente_serializer = Paciente_Serializer(paciente)
        return Response(paciente_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe el id_terminal
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Comprobamos que existe id_tipo_modalidad_paciente
        id_modalidad_paciente = Tipo_Modalidad_Paciente.objects.get(pk=request.data.get("id_tipo_modalidad_paciente"))
        if id_modalidad_paciente is None:
            return Response("Error: id_modalidad_paciente")

        # Comprobamos si los datos que recibimos de persona existen
        # Doy por supuesto que en el paciente no se modifica la persona, aún así añado la funcionalidad de modificarse recibiendo el id
        id_persona = Persona.objects.get(pk=request.data.get("id_persona"))
        if id_persona is None:
            return Response("Error: id_persona")

        paciente = Paciente.objects.get(pk=kwargs["pk"])
        paciente.id_persona = id_persona
        paciente.id_terminal = id_terminal
        paciente.id_tipo_modalidad_paciente = id_modalidad_paciente
        if request.data.get("tiene_ucr") is not None:
            paciente.tiene_ucr = request.data.get("tiene_ucr")
        if request.data.get("numero_expediente") is not None:
            paciente.numero_expediente = request.data.get("numero_expediente")
        if request.data.get("numero_seguridad_social") is not None:
            paciente.numero_seguridad_social = request.data.get("numero_seguridad_social")
        if request.data.get("prestacion_otros_servicios_sociales") is not None:
            paciente.prestacion_otros_servicios_sociales = request.data.get("prestacion_otros_servicios_sociales")
        if request.data.get("observaciones_medicas") is not None:
            paciente.observaciones_medicas = request.data.get("observaciones_medicas")
        if request.data.get("intereses_y_actividades") is not None:
            paciente.intereses_y_actividades = request.data.get("intereses_y_actividades")

        paciente.save()

        # Devolvemos el paciente modificado
        paciente_serializer = Paciente_Serializer(paciente)
        return Response(paciente_serializer.data)




class Tipo_Modalidad_Paciente_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Tipo_Modalidad_Paciente.objects.all()
    serializer_class = Tipo_Modalidad_Paciente_Serializer
    permission_classes = [IsTeacherMember]
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]


class Recursos_Comunitarios_En_Alarma_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Recursos_Comunitarios_En_Alarma.objects.all()
    serializer_class = Recursos_Comunitarios_En_Alarma_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    # Obtenemos el listado de recursos_comunitarios_en_alarma filtrado por los parametros GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Recursos_Comunitarios_En_Alarma.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe id_alarma
        id_alarma = Alarma.objects.get(pk=request.data.get("id_alarma"))
        if id_alarma is None:
            return Response("Error: id_alarma")

        # Comprobamos que existe id_recurso_comunitario
        id_recurso_comunitario = Recurso_Comunitario.objects.get(pk=request.data.get("id_recurso_comunitario"))
        if id_recurso_comunitario is None:
            return Response("Error: id_recurso_comunitario")

        # Creamos recursos_comunitarios_en_alarma
        recursos_comunitarios_en_alarma = Recursos_Comunitarios_En_Alarma(
            fecha_registro=request.data.get("fecha_registro"),
            persona=request.data.get("persona"),
            acuerdo_alcanzado=request.data.get("acuerdo_alcanzado"),
            id_alarma=id_alarma,
            id_recurso_comunitario=id_recurso_comunitario
        )

        recursos_comunitarios_en_alarma.save()

        # Devolvemos el recursos_comunitario_en_alarma creado
        recursos_comunitarios_en_alarma_serializer = Recursos_Comunitarios_En_Alarma_Serializer \
            (recursos_comunitarios_en_alarma)
        return Response(recursos_comunitarios_en_alarma_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe id_alarma
        id_alarma = Alarma.objects.get(pk=request.data.get("id_alarma"))
        if id_alarma is None:
            return Response("Error: id_alarma")

        # Comprobamos que existe id_recurso_comunitario
        id_recurso_comunitario = Recurso_Comunitario.objects.get(pk=request.data.get("id_recurso_comunitario"))
        if id_recurso_comunitario is None:
            return Response("Error: id_recurso_comunitario")

        recursos_comunitarios_en_alarma = Recursos_Comunitarios_En_Alarma.objects.get(pk=kwargs["pk"])
        if request.data.get("fecha_registro") is not None:
            recursos_comunitarios_en_alarma.fecha_registro = request.data.get("fecha_registro")
        if request.data.get("persona") is not None:
            recursos_comunitarios_en_alarma.persona = request.data.get("persona")
        if request.data.get("acuerdo_alcanzado") is not None:
            recursos_comunitarios_en_alarma.acuerdo_alcanzado = request.data.get("acuerdo_alcanzado")
        recursos_comunitarios_en_alarma.id_alarma = id_alarma
        recursos_comunitarios_en_alarma.id_recurso_comunitario = id_recurso_comunitario

        recursos_comunitarios_en_alarma.save()

        # Devolvemos el recursos_comunitario_en_alarma modificado
        recursos_comunitarios_en_alarma_serializer = Recursos_Comunitarios_En_Alarma_Serializer \
            (recursos_comunitarios_en_alarma)
        return Response(recursos_comunitarios_en_alarma_serializer.data)


class Alarma_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las alarmas
    """
    #Constantes de notificación
    ACTION_NEW_ALARM = 'new_alarm'
    ACTION_ALARM_ASSIGNMENT = 'alarm_assignment'

    queryset = Alarma.objects.all()
    serializer_class = Alarma_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Alarma.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Definimos el metodo para crear la alarma
    def create(self, request, *args, **kwargs):
        # Comprobamos que existe id_tipo_alarma
        id_tipo_alarma = Tipo_Alarma.objects.get(pk=request.data.get("id_tipo_alarma"))
        if id_tipo_alarma is None:
            return Response("Error: id_tipo_alarma")

        # Como hay dos formas de crear una alarma, dependiendo el parametro que recibamos
        # creamos la alarma de una forma u otra
        if request.data.get("id_terminal") is not None:
            id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
            if id_terminal is None:
                return Response("Error: id_terminal")

            # Creo la alarma con id_terminal
            alarma = Alarma(
                id_tipo_alarma=id_tipo_alarma,
                id_terminal=id_terminal
            )

            alarma.save()

            # Enviamos notificación a los teleoperadores a través de la app alarmas
            self.notify(alarma, self.ACTION_NEW_ALARM)

            # Devolvemos la alarma creada
            alarma_serializer = Alarma_Serializer(alarma)
            return Response(alarma_serializer.data)

        if request.data.get("id_paciente_ucr") is not None:
            id_paciente_ucr = Paciente.objects.get(pk=request.data.get("id_paciente_ucr"))
            if id_paciente_ucr is None:
                return Response("Error: id_paciente_ucr")

            # Creo la alarma con id_paciente_ucr
            alarma = Alarma(
                id_tipo_alarma=id_tipo_alarma,
                id_paciente_ucr=id_paciente_ucr
            )

            alarma.save()

            # Enviamos notificación a los teleoperadores a través de la app alarmas
            self.notify(alarma, self.ACTION_NEW_ALARM)

            # Devolvemos la alarma creada y notificamos a los clientes
            alarma_serializer = Alarma_Serializer(alarma)
            return Response(alarma_serializer.data)

    # TODO id_teleoperador se añade por JSON
    def update(self, request, *args, **kwargs):
        # Obtenemos la alarma a modificar
        alarma = Alarma.objects.get(pk=kwargs["pk"])

        # Guardamos teleoperador antiguo
        old_id = alarma.id_teleoperador

        # Obtenemos el id_teleoperador que ateiende la alarma
        # Este id sera el del usuario
        id_teleoperador = User.objects.get(pk=request.data.get("id_teleoperador"))
        if id_teleoperador is None:
           return Response("Error: id_teleoperador")

        alarma.id_teleoperador = id_teleoperador
        if request.data.get("estado_alarma") is not None:
            alarma.estado_alarma = request.data.get("estado_alarma")
        if request.data.get("observaciones") is not None:
            alarma.observaciones = request.data.get("observaciones")
        if request.data.get("resumen") is not None:
            alarma.resumen = request.data.get("resumen")

        alarma.save()

        # Notificamos si es una asignación (el id_teleoperador era null y ahora no)
        if old_id is None and id_teleoperador is not None:
            self.notify(alarma, self.ACTION_ALARM_ASSIGNMENT)

        # Devolvemos la alarma modificada
        alarma_serializer = Alarma_Serializer(alarma)
        return Response(alarma_serializer.data)


    def notify(self, alarma, accion):
        alarma_serializer = Alarma_Serializer(alarma)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'teleoperadores',
            {"type": "notify.clients", "action": accion, "alarma": alarma_serializer.data},
        )


class Dispositivos_Auxiliares_en_Terminal_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Dispositivos_Auxiliares_En_Terminal.objects.all()
    serializer_class = Dispositivos_Auxiliares_en_Terminal_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Dispositivos_Auxiliares_En_Terminal.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe id_terminal
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Comprobamos que existe id_tipo_alarma
        id_tipo_alarma = Tipo_Alarma.objects.get(pk=request.data.get("id_tipo_alarma"))
        if id_tipo_alarma is None:
            return Response("Error: id_tipo_alarma")

        # Creamos el dispositivos_auxiliares_en_terminal
        dispositivos_auxiliares_en_terminal = Dispositivos_Auxiliares_En_Terminal(
            id_terminal=id_terminal,
            id_tipo_alarma=id_tipo_alarma
        )

        dispositivos_auxiliares_en_terminal.save()

        # Devolvemos el dispositivos_auxiliares_en_terminal creado
        dispositivos_auxiliares_en_terminal_serializer = Dispositivos_Auxiliares_en_Terminal_Serializer \
            (dispositivos_auxiliares_en_terminal)
        return Response(dispositivos_auxiliares_en_terminal_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe id_terminal
        id_terminal = Terminal.objects.get(pk=request.data.get("id_terminal"))
        if id_terminal is None:
            return Response("Error: id_terminal")

        # Comprobamos que existe id_tipo_alarma
        id_tipo_alarma = Tipo_Alarma.objects.get(pk=request.data.get("id_tipo_alarma"))
        if id_tipo_alarma is None:
            return Response("Error: id_tipo_alarma")

        dispositivos_auxiliares_en_terminal = Dispositivos_Auxiliares_En_Terminal.objects.get(pk=kwargs["pk"])
        dispositivos_auxiliares_en_terminal.id_terminal = id_terminal
        dispositivos_auxiliares_en_terminal.id_tipo_alarma = id_tipo_alarma

        dispositivos_auxiliares_en_terminal.save()

        # Devolvemos el dispositivos_auxiliares_en_terminal modificado
        dispositivos_auxiliares_en_terminal_serializer = Dispositivos_Auxiliares_en_Terminal_Serializer \
            (dispositivos_auxiliares_en_terminal)
        return Response(dispositivos_auxiliares_en_terminal_serializer.data)


class Centro_Sanitario_En_Alarma_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Centro_Sanitario_En_Alarma.objects.all()
    serializer_class = Centro_Sanitario_En_Alarma_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Centro_Sanitario_En_Alarma.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe id_alarma
        id_alarma = Alarma.objects.get(pk=request.data.get("id_alarma"))
        if id_alarma is None:
            return Response("Error: id_alarma")

        # Comprobamos que existe id_centro_sanitario
        id_centro_sanitario = Centro_Sanitario.objects.get(pk=request.data.get("id_centro_sanitario"))
        if id_centro_sanitario is None:
            return Response("Error: id_centro_sanitario")

        centro_sanitario_en_alarma = Centro_Sanitario_En_Alarma(
            fecha_registro=request.data.get("fecha_registro"),
            persona=request.data.get("persona"),
            acuerdo_alcanzado=request.data.get("acuerdo_alcanzado"),
            id_alarma=id_alarma,
            id_centro_sanitario=id_centro_sanitario
        )
        centro_sanitario_en_alarma.save()

        # Devolvemos el centro_sanitario_en_alarma creado
        centro_sanitario_en_alarma_serializer = Centro_Sanitario_En_Alarma_Serializer(centro_sanitario_en_alarma)
        return Response(centro_sanitario_en_alarma_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe id_alarma
        id_alarma = Alarma.objects.get(pk=request.data.get("id_alarma"))
        if id_alarma is None:
            return Response("Error: id_alarma")

        # Comprobamos que existe id_centro_sanitario
        id_centro_sanitario = Centro_Sanitario.objects.get(pk=request.data.get("id_centro_sanitario"))
        if id_centro_sanitario is None:
            return Response("Error: id_centro_sanitario")

        centro_sanitario_en_alarma = Centro_Sanitario_En_Alarma.objects.get(pk=kwargs["pk"])
        if request.data.get("fecha_registro") is not None:
            centro_sanitario_en_alarma.fecha_registro = request.data.get("fecha_registro")
        if request.data.get("persona") is not None:
            centro_sanitario_en_alarma.persona = request.data.get("persona")
        if request.data.get("acuerdo_alcanzado") is not None:
            centro_sanitario_en_alarma.acuerdo_alcanzado = request.data.get("acuerdo_alcanzado")
        centro_sanitario_en_alarma.id_alarma = id_alarma
        centro_sanitario_en_alarma.id_centro_sanitario = id_centro_sanitario

        centro_sanitario_en_alarma.save()

        # Devolvemos el centro_sanitario_en_alarma creado
        centro_sanitario_en_alarma_serializer = Centro_Sanitario_En_Alarma_Serializer(centro_sanitario_en_alarma)
        return Response(centro_sanitario_en_alarma_serializer.data)




class Persona_Contacto_En_Alarma_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Persona_Contacto_En_Alarma.objects.all()
    serializer_class = Persona_Contacto_En_Alarma_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Persona_Contacto_En_Alarma.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos que existe la alarma
        id_alarma = Alarma.objects.get(pk=request.data.get("id_alarma"))
        if id_alarma is None:
            return Response("Error: id_alarma")

        # Comprobamos que existe la persona de contacto
        id_persona_contacto = Persona.objects.get(pk=request.data.get("id_persona_contacto"))
        if id_persona_contacto is None:
            return Response("Error: id_persona_contacto")

        persona_contacto_en_alarma = Persona_Contacto_En_Alarma(
            id_alarma=id_alarma,
            id_persona_contacto=id_persona_contacto,
            fecha_registro=request.data.get("fecha_registro"),
            acuerdo_alcanzado=request.data.get("acuerdo_alcanzado")
        )

        persona_contacto_en_alarma.save()
        # Devolvemos persona de contacto en alarma creado
        persona_contacto_en_alarma_serializer = Persona_Contacto_En_Alarma_Serializer(persona_contacto_en_alarma)
        return Response(persona_contacto_en_alarma_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos que existe la alarma
        id_alarma = Alarma.objects.get(pk=request.data.get("id_alarma"))
        if id_alarma is None:
            return Response("Error: id_alarma")

        # Comprobamos que existe la persona de contacto
        id_persona_contacto = Persona.objects.get(pk=request.data.get("id_persona_contacto"))
        if id_persona_contacto is None:
            return Response("Error: id_persona_contacto")

        persona_contacto_en_alarma = Persona_Contacto_En_Alarma.objects.get(pk = kwargs["pk"])
        persona_contacto_en_alarma.id_alarma = id_alarma
        persona_contacto_en_alarma.id_persona_contacto = id_persona_contacto
        if request.data.get("fecha_registro") is not None:
            persona_contacto_en_alarma.fecha_registro = request.data.get("fecha_registro")
        if request.data.get("acuerdo_alcanzado") is not None:
            persona_contacto_en_alarma.acuerdo_alcanzado = request.data.get("acuerdo_alcanzado")

        persona_contacto_en_alarma.save()

        persona_contacto_en_alarma
        # Devolvemos persona de contacto en alarma creado
        persona_contacto_en_alarma_serializer = Persona_Contacto_En_Alarma_Serializer(persona_contacto_en_alarma)
        return Response(persona_contacto_en_alarma_serializer.data)


class Relacion_Usuario_Centro_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    queryset = Relacion_Usuario_Centro.objects.all()
    serializer_class = Relacion_Usuario_Centro_Serializer
    # permission_classes = [permissions.IsAdminUser] # Si quisieramos para todos los registrados: IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Hacemos una búsqueda por los valores introducidos por parámetros
        query = getQueryAnd(request.GET)
        if query:
            queryset = Relacion_Usuario_Centro.objects.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Comprobamos si existe el id_paciente
        id_paciente = Paciente.objects.get(pk=request.data.get("id_paciente"))
        if id_paciente is None:
            return Response("Error: id_paciente")

        # Comprobamos si existe el id_centro_sanitario
        id_centro_sanitario = Centro_Sanitario.objects.get(pk=request.data.get("id_centro_sanitario"))
        if id_centro_sanitario is None:
            return Response("Error: id_centro_sanitario")

        relacion_usuario_centro = Relacion_Usuario_Centro(
            persona_contacto=request.data.get("persona_contacto"),
            distancia=request.data.get("distancia"), # Viene en km
            tiempo=request.data.get("tiempo"), # Viene en minutos
            observaciones=request.data.get("observaciones"),
            id_paciente=id_paciente,
            id_centro_sanitario=id_centro_sanitario
        )

        relacion_usuario_centro.save()

        # Devolvemos la relacion_usuario_centro creada
        relacion_usuario_centro_serializer = Relacion_Usuario_Centro_Serializer(relacion_usuario_centro)
        return Response(relacion_usuario_centro_serializer.data)

    def update(self, request, *args, **kwargs):
        # Comprobamos si existe el id_paciente
        id_paciente = Paciente.objects.get(pk=request.data.get("id_paciente"))
        if id_paciente is None:
            return Response("Error: id_paciente")

        # Comprobamos si existe el id_centro_sanitario
        id_centro_sanitario = Centro_Sanitario.objects.get(pk=request.data.get("id_centro_sanitario"))
        if id_centro_sanitario is None:
            return Response("Error: id_centro_sanitario")

        relacion_usuario_centro = Relacion_Usuario_Centro.objects.get(pk=kwargs["pk"])
        if request.data.get("persona_contacto") is not None:
            relacion_usuario_centro.persona_contacto = request.data.get("persona_contacto")
        if request.data.get("distancia") is not None:
            relacion_usuario_centro.distancia = request.data.get("distancia")
        if request.data.get("tiempo") is not None:
            relacion_usuario_centro.tiempo = request.data.get("tiempo")
        if request.data.get("observaciones") is not None:
            relacion_usuario_centro.observaciones = request.data.get("observaciones")
        relacion_usuario_centro.id_paciente = id_paciente
        relacion_usuario_centro.id_centro_sanitario = id_centro_sanitario
        relacion_usuario_centro.save()

        # Devolvemos la relacion_usuario_centro modificada
        relacion_usuario_centro_serializer = Relacion_Usuario_Centro_Serializer(relacion_usuario_centro)
        return Response(relacion_usuario_centro_serializer.data)

class Gestion_Base_Datos_ViewSet(viewsets.ModelViewSet):
    """
    Gestion de la base de datos
    """
    queryset = Gestion_Base_Datos.objects.all().order_by('-fecha_copia')
    serializer_class = Gestion_Base_Datos_Serializer

    def create(self, request, *args, **kwargs):
        base_datos = Gestion_Base_Datos(
            ubicacion_copia = '',
            fecha_copia = datetime.today().strftime('%Y-%m-%d'),
            descripcion_copia = request.data.get("descripcion_copia")
        )
        #En caso de que el usuario no introduzca nada introducimos un mensaje por defecto.
        if base_datos.descripcion_copia is None:
            base_datos.descripcion_copia = 'Copia sin descripción.'
        base_datos.save()

        # Obtenemos la ruta que nos interesa y la pasamos a string para poder editarla facilmente
        rutaAct = str(Path(__file__).resolve().parent.parent.parent)
        rutaBackup = rutaAct+'\\backup\\'
        #Obtenemos el ID, el cual usamos para el nombre de la copia.
        id_b = str(base_datos.id)
        #base_datos.ubicacion_copia =
        base_datos.ubicacion_copia = '\\backup\\'+'db.sqlite3'+id_b
        # Devolvemos la base_datos creada - base_datos_serializer = Gestion_Base_Datos_Serializer(base_datos)
        base_datos.save()

        #Comprobar si existe la base de datos original
        if os.path.isfile(rutaAct+'\\db.sqlite3'):
            #Obtenemos la ruta donde esta la base de datos y la que queremos original a partir de esta, shutil lo copia.
            source = rutaAct+'\\db.sqlite3'
            destination = rutaBackup+'db.sqlite3'+id_b
            shutil.copy(source, destination)
            return Response("Copia de la base de datos creada correctamente con id: "+id_b)

        return Response("La copia de la base de datos no ha podido ser creada.", status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        #Conseguimos el parametro de la URL
        parametro = ((kwargs["pk"]))
        #En caso de que tenga alguna x se la quitamos
        parametro_res = parametro.lstrip("x")
        #Variables con las rutas por defecto, seran editadas en los condicionales, son dos para aclaración de la funcion shutil
        source = str(Path(__file__).resolve().parent.parent.parent) + '\\backup\\db.sqlite3'
        destination = str(Path(__file__).resolve().parent.parent.parent)

        #Condicional, para que en caso de pasarle algo que no sea un id, como ara en 2/3 funcionalidades, no nos de fallo.
        if parametro != 'restore':
            base_datos = Gestion_Base_Datos.objects.all().get(pk=parametro_res)
        else:
            base_datos = Gestion_Base_Datos.objects.all()
        #Si el parametro que le pasamos en la URL es restore, y existe la copia solo con el ADM(Se debe generar),
        #entonces restauramos esta base de datos.
        if str(parametro) == 'restore':
            if os.path.isfile(source+'_adm'):
                source_res = source+'_adm'
                shutil.copy(source_res, destination+'\\db.sqlite3')
                return Response("La base de datos ha sido restaurada solo con la cuenta de Administrador.")
            else:
                return Response("La copia de la base de datos con id: " + parametro + " seleccionada no existe.", status=status.HTTP_400_BAD_REQUEST)
        #En caso de que tengamos cualquier otra cosa que no sea una x+id, simplemente no entrara en el if
        #En caso afirmativo, entrara y copiara la base de datos con el id indicadp.
        if (kwargs["pk"])[:1] == 'x':
            if os.path.isfile(source+parametro_res):
                source_r = source+str(parametro_res)
                shutil.copy(source_r, destination+'\\db.sqlite3')
                return Response("La base de datos con id: "+parametro_res+" ha sido restaurada correctamente.")
            else:
                return Response("La copia de la base de datos con id: " + parametro + " seleccionada no existe.", status=status.HTTP_400_BAD_REQUEST)
        #Comprobamos si existe copia con el id pasado en la URL, si es asi, lo borramos.
        if os.path.isfile(source+parametro_res):
            os.remove(source+parametro_res)
            # Borramos la entrada de la API-RES
            base_datos.delete()
            return Response("La copia de la base de datos con id: "+parametro+" ha sido borrada correctamente.")
        else:
            base_datos.delete()

        #Respuesta de error por defecto.
        return Response("La copia de la base de datos con id: "+parametro+" seleccionada no existe.", status=status.HTTP_400_BAD_REQUEST)


'''{
               "id": "1",
               "nombre": "pepe",
               "apellido": "grillo",
               "sexo": "Hombre",
               "telefono": "664489164",
               "localidad": "Plasencia",
               "provincia": "Cáceres",
               "centro_de_salud":" centro de slaud la data",
               "Hospital":"Hospital de Plasencia",
               "Guardia Civil":"Guardia civil de plasencia",
               "Policia":"Policia Local Plasencia",
               "Bomberos":"Bomberos de Plasencia",
               "Servicios Sociales":"Servicios Sociales de Plasencia",
               "Cruz Roja":"Cruz Roja de Plasencia",

           },
           {
               "id": "1",
               "nombre": "María",
               "apellido": "Gil",
               "sexo": "Mujer",
               "telefono": "664428142",
               "localidad": "Coria",
               "provincia": "Cáceres",
               "centro_de_salud": " centro de salud de Coria",
               "Hospital": "Hospital de Coria",
               "Guardia Civil": "Guardia civil de Coria",
               "Policia": "Policia Local Coria",
               "Bomberos": "Bomberos de Coria",
               "Servicios Sociales": "Servicios Sociales de Coria",
               "Cruz Roja": "Cruz Roja de Coria",

               },
               '''
class DesarrolladorTecnologiaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para las empresas
    """
    authentication_classes = []
    permission_classes = (permissions.AllowAny, )
    queryset = Convocatoria_Proyecto.objects.all()
    serializer_class = Convocatoria_Proyecto_Serializer
    http_method_names=['get']
