import os
from django.db import models
from model_utils import Choices
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from utilidad.logging import info, error, blue

# Para tratamiento de imagenes
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.core.files.base import ContentFile

# Create your models here.


class Logs_AccionesUsuarios(models.Model):
    """
    Modelo que gaurdará todos los logs relativos a la api-rest.
    """
    METODOS_HTTP_ENUM = Choices("GET", "POST", "PUT", "DELETE")

    timestamp = models.DateTimeField(null=False, default=now)
    direccion_ip = models.CharField(null=False, max_length=40)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    ruta = models.TextField(null=False, default="")
    query = models.TextField(null=False, default="")
    metodo_http = models.CharField(null=False, choices=METODOS_HTTP_ENUM, max_length=6)
    estado_http = models.CharField(null=False, max_length=10)
    # TODO: metadatos adicionales -> ubicacion, navegador, etc

    def __str__(self):
        return "[LOG_Accion][%s] '%s' @ [%s] [%s] || %s %s%s => %s" % (
            self.id, self.user.username, self.direccion_ip, self.timestamp,
            self.metodo_http, self.ruta, self.query, self.estado_http
        )

class Logs_ConexionesUsuarios(models.Model):
    """
    Modelo que guarda los registros de todos los inicios de sesión e intentos de conexión al sistema.
    """
    TIPO_LOGIN_ENUM = Choices("PANEL_ADMIN", "TOKEN_API", "OTRO")

    timestamp = models.DateTimeField(null=False, default=now)
    direccion_ip = models.CharField(null=False, max_length=40)

    username = models.CharField(null=False, max_length=150)
    login_correcto = models.BooleanField(null=False, default=False)
    tipo_login = models.CharField(null=False, choices=TIPO_LOGIN_ENUM, max_length=15)
    # TODO: metadatos adicionales -> ubicacion, navegador, etc

    def __str__(self):
        return "[LOG_Sesion][%s] '%s' @ [%s] [%s] || [%s] Login Correcto: %s" % (
            self.id, self.username, self.direccion_ip, self.timestamp,
            self.tipo_login, self.login_correcto
        )


# Creamos la clase imagen con los atributos usuario e imagen
class Imagen_User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagen_usuario', null=True, blank=True, default="")

    def save(self, *args, **kwargs):
        # Si se ha actualizado (no nueva), borrar la imagen vieja.
        instancia_vieja = Imagen_User.objects.filter(pk=self.pk).first()
        if instancia_vieja and instancia_vieja.imagen != self.imagen:
            if os.path.exists(instancia_vieja.imagen.path):
                os.remove(instancia_vieja.imagen.path)

        # Intentamos minificar la imagen
        try:
            self._minificar()
        except Exception as e:
            error(f"Fallo al intentar minificar imagen: {e}")

        # Dejamos que django termine de persistir el modelo
        super(Imagen_User, self).save(*args, **kwargs)

    def _minificar(self):
        """
        Minifica la imagen para ahorrar espacio y aligerar la carga del servidor
        """
        if self.imagen:
            # Sacar ajustes de calidad de imagen
            size = settings.MINIFICATION_SIZE
            quality = settings.MINIFICATION_QUALITY

            # Abrimos la imagen con Pillow, pasamos a RGB (para JPEG) y minificamos
            # Lo abrimos con un ContentFile, porque el fichero está en memoria y no en disco
            img = Image.open(ContentFile(self.imagen.read())).convert('RGB')
            img.thumbnail(size)

            # Creamos un buffer donde escribir la imagen transformada
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=quality, optimize=True)
            img_bytes.seek(0)  # Mover el cursor al principio

            # Guardamos el buffer a un fichero
            filename = f"{self.user.username}.jpg"
            self.imagen.save(filename, File(img_bytes, name=filename), save=False)


# Creamos la clase que almacena la relación entre el usuario y la base de datos a la que pertenece
class Database(models.Model):
    nameDescritive = models.CharField(max_length=200)
    engine = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    user = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True, null=True)
    host = models.CharField(max_length=200, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.nameDescritive+": "+self.name+" - "+self.engine

class Database_User(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   database = models.ForeignKey(Database, on_delete=models.CASCADE)

   def __str__(self):
        return self.database.nameDescritive+": "+self.user.username+" - "+self.database.name

class Tipo_Agenda(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=100)
    IMPORTANCIA_ENUM = Choices("Alta","Baja")
    importancia = models.CharField(choices=IMPORTANCIA_ENUM, default=IMPORTANCIA_ENUM.Baja, max_length=20)
    def __str__(self):
        return self.nombre+" - "+self.importancia+" Prioridad:"+" - "+str(self.codigo)


class Direccion(models.Model):
    localidad = models.CharField(max_length=200, null=False)
    provincia = models.CharField(max_length=200, null=False)
    direccion = models.CharField(max_length=200, null=False)
    codigo_postal = models.CharField(max_length=200, null=False)
    def __str__(self):
        return self.localidad+" "+self.provincia+" "+self.direccion+" "+self.codigo_postal

class Clasificacion_Alarma(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    codigo = models.CharField(max_length=200)
    def __str__(self):
        return self.nombre+" "+self.codigo

class Tipo_Alarma(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    codigo = models.CharField(max_length=200)
    id_clasificacion_alarma = models.ForeignKey(Clasificacion_Alarma, null=True, on_delete=models.SET_NULL)
    es_dispositivo = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre+" - "+self.codigo


class Clasificacion_Recurso_Comunitario(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    def __str__(self):
        return self.nombre

class Tipo_Recurso_Comunitario(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    id_clasificacion_recurso_comunitario = models.ForeignKey(Clasificacion_Recurso_Comunitario, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.nombre

class Recurso_Comunitario(models.Model):
    nombre = models.CharField(max_length=500, blank=True)
    id_tipos_recurso_comunitario = models.ForeignKey(Tipo_Recurso_Comunitario, null=True, on_delete=models.SET_NULL)
    id_direccion = models.ForeignKey(Direccion, null=True, on_delete=models.SET_NULL)
    telefono = models.CharField(max_length=20)
    def __str__(self):
        if self.id_tipos_recurso_comunitario and self.id_direccion:
            return self.nombre + " - "+self.id_tipos_recurso_comunitario.nombre+" - "+self.id_direccion.localidad
        elif self.id_tipos_recurso_comunitario:
            return self.nombre + " - "+self.id_tipos_recurso_comunitario.nombre
        else:
            return self.nombre + " - "+self.id_direccion.localidad

class Persona(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    apellidos = models.CharField(max_length=200, null=False)
    dni = models.CharField(max_length=20, null=False)
    fecha_nacimiento = models.DateField(blank=True)
    SEXO_ENUM = Choices("Hombre", "Mujer")
    sexo = models.CharField(choices=SEXO_ENUM, default=SEXO_ENUM.Hombre, max_length=20)
    telefono_fijo = models.CharField(max_length=20, blank=True)
    telefono_movil = models.CharField(max_length=20, blank=True)
    id_direccion = models.ForeignKey(Direccion, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.nombre+" "+self.apellidos+" "+self.dni

class Tipo_Modalidad_Paciente(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    id_terminal = models.ForeignKey('Terminal', null=True, on_delete=models.SET_NULL)
    id_persona = models.ForeignKey(Persona, null=True, on_delete=models.SET_NULL)
    tiene_ucr = models.BooleanField(null=False, default=False)
    numero_expediente = models.CharField(max_length=200, blank=True)
    numero_seguridad_social = models.CharField(max_length=200, null=False)
    prestacion_otros_servicios_sociales = models.CharField(max_length=2000, blank=True)
    observaciones_medicas = models.CharField(max_length=6000, null=False, blank=True)
    intereses_y_actividades = models.CharField(max_length=6000, null=False, blank=True)
    id_tipo_modalidad_paciente = models.ForeignKey(Tipo_Modalidad_Paciente, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        if self.id_terminal:
            return self.id_persona.nombre+" "+self.id_persona.apellidos+" "+self.id_persona.dni+" Terminal:"+self.id_terminal.numero_terminal #TODO: Poner también el número de Terminal
        else:
            return self.id_persona.nombre

class Relacion_Paciente_Persona(models.Model):
    id_paciente = models.ForeignKey(Paciente, null=True, on_delete=models.SET_NULL)
    nombre = models.CharField(max_length=200, null=False)
    apellidos = models.CharField(max_length=200, null=False)
    telefono = models.CharField(max_length=20, blank=True)
    tipo_relacion = models.CharField(max_length=200, null=False)
    tiene_llaves_vivienda = models.BooleanField(default=False, blank=True)
    disponibilidad = models.CharField(max_length=200, blank=True)
    observaciones = models.CharField(max_length=4000, blank=True)
    prioridad = models.IntegerField( blank=True)
    es_conviviente= models.BooleanField(default=False)
    tiempo_domicilio = models.IntegerField(default=1)
    def __str__(self):
        if self.id_paciente and self.id_paciente.id_persona:
            return "Paciente: "+self.id_paciente.id_persona.nombre+" - Contacto: "+self.nombre+" "+self.apellidos
        else:
            return "Contacto: "+self.nombre+" "+self.apellidos


class Tipo_Vivienda(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    def __str__(self):
        return self.nombre

class Tipo_Situacion(models.Model):
    nombre = models.CharField(max_length=200)
    def __str__(self):
        return self.nombre

class Terminal(models.Model):
    numero_terminal = models.CharField(max_length=30, null=False)
    id_titular = models.ForeignKey(Paciente, null=True, on_delete=models.PROTECT, blank=True)
    id_tipo_vivienda = models.ForeignKey(Tipo_Vivienda, null=True, on_delete=models.SET_NULL)
    modo_acceso_vivienda = models.CharField(max_length=400)
    barreras_arquitectonicas = models.CharField(max_length=5000, blank=True)
    modelo_terminal = models.CharField(max_length=400, blank=True)
    id_tipo_situacion = models.ForeignKey(Tipo_Situacion, null=True, on_delete=models.SET_NULL)
    fecha_tipo_situacion = models.DateField(null=True, default=now)
    def __str__(self):
        if self.id_titular:
            return self.numero_terminal+" - "+self.id_titular.id_persona.nombre
        else:
            return self.numero_terminal




class Relacion_Terminal_Recurso_Comunitario(models.Model):
    id_terminal = models.ForeignKey(Terminal, null=True, on_delete=models.SET_NULL)
    id_recurso_comunitario = models.ForeignKey(Recurso_Comunitario, null=True, on_delete=models.SET_NULL)
    tiempo_estimado = models.IntegerField(default=1)


class Agenda(models.Model):
    id_paciente = models.ForeignKey(Paciente, null=True, on_delete=models.SET_NULL)
    id_tipo_agenda = models.ForeignKey(Tipo_Agenda, null=True, on_delete=models.SET_NULL)
    fecha_registro = models.DateTimeField(null=False, default=now)
    fecha_prevista = models.DateTimeField(null=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    observaciones = models.CharField(max_length=4000, blank=True)
    def __str__(self):
        if self.id_tipo_agenda:
            return self.id_paciente.id_persona.nombre+" "+self.id_paciente.id_persona.apellidos+" "+self.id_paciente.id_persona.dni+" - "+self.id_tipo_agenda.nombre
        else:
            return self.id_paciente.id_persona.nombre+" "+self.id_paciente.id_persona.apellidos+" "+self.id_paciente.id_persona.dni


class Historico_Agenda_Llamadas(models.Model):
    id_agenda = models.ForeignKey(Agenda, null=True, on_delete=models.SET_NULL, related_name="historico_agenda")
    id_teleoperador = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) #OJO: User de los modelos de admin.
    observaciones = models.CharField(max_length=4000, blank=True)
    def __str__(self):
        if self.id_agenda and self.id_agenda.id_paciente and self.id_teleoperador:
            return self.id_agenda.id_paciente.id_persona.nombre+" - "+self.id_teleoperador.username
        elif self.id_agenda and self.id_agenda.id_paciente:
            return self.id_agenda.id_paciente.id_persona.nombre

class Dispositivos_Auxiliares_En_Terminal (models.Model):
    id_terminal = models.ForeignKey(Terminal, null=True, on_delete=models.SET_NULL)
    id_tipo_alarma = models.ForeignKey(Tipo_Alarma, null=True, on_delete=models.SET_NULL)



class Alarma(models.Model):
    id_tipo_alarma = models.ForeignKey(Tipo_Alarma, null=True, on_delete=models.SET_NULL)
    ESTADO_ENUM = Choices("Abierta", "Cerrada")
    estado_alarma = models.CharField(choices=ESTADO_ENUM, default=ESTADO_ENUM.Abierta, max_length=20)
    fecha_registro = models.DateTimeField(null=False, default=now)
    id_teleoperador = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, blank=True) # OJO: User de los modelos de admin.
    id_paciente_ucr = models.ForeignKey(Paciente, null=True, on_delete=models.SET_NULL, blank=True)  # OJO: Puede ser null si no lo avisó un paciente
    id_terminal = models.ForeignKey(Terminal, null=True, on_delete=models.SET_NULL, blank=True)  # OJO: Puede ser null si no lo avisó un terminal
    observaciones = models.CharField(max_length=10000, blank=True)
    resumen = models.CharField(max_length=10000, blank=True)
    def __str__(self):
        if self.id_tipo_alarma:
            return self.id_tipo_alarma.nombre + " - " + self.estado_alarma + " - " + str(self.fecha_registro)
        else:
            return self.estado_alarma+ " - " + str(self.fecha_registro)

    def save(self, *args, **kwargs):
        # Si no tiene asignada una cave primaria, es una nueva instancia
        is_new = self.pk is None

        # Ejecutar el resto del código original
        super(Alarma, self).save(*args, **kwargs)

        # Si es nuevo, notificar
        if is_new:
            # Notificar a los clientes
            self.notify('new_alarm')

    def notify(self, accion):
        from .rest_django.serializers import Alarma_Serializer

        alarma_serializer = Alarma_Serializer(self)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'teleoperadores',
            {"type": "notify.clients", "action": accion, "alarma": alarma_serializer.data},
        )

     
class Alarma_Programada(models.Model):
    """
    Plantilla para generar una alarma al ser disparada.
    """
    id_tipo_alarma = models.ForeignKey(Tipo_Alarma, null=True, on_delete=models.SET_NULL)
    fecha_registro = models.DateTimeField(null=False, default=now) # Momento en el que la alarma se disparará
    
    id_paciente_ucr = models.ForeignKey(Paciente, null=True, on_delete=models.SET_NULL, blank=True)  # OJO: Puede ser null si no lo avisó un paciente
    id_terminal = models.ForeignKey(Terminal, null=True, on_delete=models.SET_NULL, blank=True)      # OJO: Puede ser null si no lo avisó un terminal
    def __str__(self):
        return "[Programada] %s - %s" % (self.id_tipo_alarma.nombre, str(self.fecha_registro))

    def disparar(self):
        """
        Dispara y genera una Alarma a partir de los datos de la Alarma_Programada, borrando a esta última de la BBDD.
        """
        try:
            # Guardar la alarma
            alarma_disparada = Alarma(
                id_tipo_alarma=self.id_tipo_alarma,
                fecha_registro=self.fecha_registro,
                id_paciente_ucr=self.id_paciente_ucr,
                id_terminal=self.id_terminal
            )
            alarma_disparada.save()
            # Y borrar la programada
            self.delete()
            blue("TeleasistenciaApp", f"Alarma Disparada: {self}")
        except Exception as e:
            error("TeleasistenciaApp", f"Hubo un error al disparar la alarma: {e}")

class Persona_Contacto_En_Alarma(models.Model):
    id_alarma = models.ForeignKey(Alarma, null=True, on_delete=models.SET_NULL)
    id_persona_contacto = models.ForeignKey(Relacion_Paciente_Persona, null=True, on_delete=models.SET_NULL)
    fecha_registro = models.DateTimeField(null=False, default=now)
    def __str__(self):
        return self.id_alarma.id_tipo_alarma.nombre+" - "+self.id_alarma.estado_alarma+" - "+str(self.id_alarma.fecha_registro)+" "+self.id_persona_contacto.nombre+" - "+str(self.fecha_registro)

class Recursos_Comunitarios_En_Alarma(models.Model):
    id_alarma = models.ForeignKey(Alarma, null=True, on_delete=models.SET_NULL)
    id_recurso_comunitario = models.ForeignKey(Recurso_Comunitario, null=True, on_delete=models.SET_NULL)
    fecha_registro = models.DateTimeField(null=False, default=now)
    def __str__(self):
        if self.id_alarma and self.id_alarma.id_tipo_alarma:
            return self.id_alarma.id_tipo_alarma.nombre+" - "+self.id_alarma.estado_alarma+" - "+str(self.id_alarma.fecha_registro)+" - "+str(self.fecha_registro)
        elif self.id_alarma:
            return self.id_alarma.estado_alarma + " - " + str(
                self.id_alarma.fecha_registro) + " - " +" - " + str(self.fecha_registro)

class Gestion_Base_Datos(models.Model):
    ubicacion_copia = models.CharField(max_length=200, default='/Server/teleasistencia/backup')
    fecha_copia = models.DateField(null=False, default=now)
    descripcion_copia = models.CharField(max_length=300, null=True, default='Copia sin descripcion.')
    def __str__(self):
        return self.ubicacion_copia+" - "+self.fecha_copia+" - "+self.descripcion_copia
class Convocatoria_Proyecto(models.Model):
    convocatoria = models.CharField(max_length=1000, blank=True)
    fecha = models.DateField(null=False, default=now)
    def __str__(self):
        return self.convocatoria
class Desarrollador(models.Model):
    # Related name nos permite obtener los datos relacionados desde la entidad a la que hace referencia
    id_convocatoria_proyecto = models.ForeignKey(Convocatoria_Proyecto, null=True, on_delete=models.SET_NULL, related_name='desarrolladores')
    nombre=models.CharField(max_length=1000, blank=True)
    descripcion=models.CharField(max_length=10000, blank=True)
    imagen=models.ImageField(upload_to='desarrollador/imagen_desarrollador', null=True, blank=True, default='')
    es_profesor= models.BooleanField(default=False)
    def __str__(self):
        return self.id_convocatoria_proyecto.convocatoria+ " - "+ self.nombre+ " - "+self.descripcion

class Tecnologia(models.Model):
    nombre = models.CharField(max_length=1000, blank=True)
    imagen = models.ImageField(upload_to='desarrollador/imagen_tecnologia', null=True, blank=True, default='')
    def __str__(self):
        return self.nombre

class Desarrollador_Tecnologia(models.Model):
    # Related name nos permite obtener los datos relacionados desde la entidad a la que hace referencia
    id_desarrollador = models.ForeignKey(Desarrollador, null=True, on_delete=models.SET_NULL, related_name='desarrollador_tecnologias')
    id_tecnologia = models.ForeignKey(Tecnologia, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.id_desarrollador.nombre+ " - "+self.id_tecnologia.nombre
