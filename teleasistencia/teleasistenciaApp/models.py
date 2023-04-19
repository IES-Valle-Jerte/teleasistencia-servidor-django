from django.db import models
from model_utils import Choices
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# Create your models here.

# Creamos la clase imagen con los atributos usuario e imagen
class Imagen_User(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   imagen = models.ImageField(upload_to='imagen_usuario', null=True, blank=True, default="")


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
    def __str__(self):
        if self.id_paciente and self.id_paciente.id_persona:
            return "Paciente: "+self.id_paciente.id_persona.nombre+" - Contacto: "+self.nombre+" "+self.apellidos
        else:
            return "Contacto: "+self.nombre+" "+self.apellidos


class Tipo_Vivienda(models.Model):
    nombre = models.CharField(max_length=200, null=False)
    def __str__(self):
        return self.nombre

class Terminal(models.Model):
    numero_terminal = models.CharField(max_length=30, null=False)
    id_titular = models.ForeignKey(Paciente, null=True, on_delete=models.PROTECT, blank=True)
    id_tipo_vivienda = models.ForeignKey(Tipo_Vivienda, null=True, on_delete=models.SET_NULL)
    modo_acceso_vivienda = models.CharField(max_length=400)
    barreras_arquitectonicas = models.CharField(max_length=5000, blank=True)
    modelo_terminal = models.CharField(max_length=400, blank=True)
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

class Persona_Contacto_En_Alarma(models.Model):
    id_alarma = models.ForeignKey(Alarma, null=True, on_delete=models.SET_NULL)
    id_persona_contacto = models.ForeignKey(Persona, null=True, on_delete=models.SET_NULL)
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


class Tipo_Situacion(models.Model):
    nombre = models.CharField(max_length=200)
    def __str__(self):
        return self.nombre

class Historico_Tipo_Situacion(models.Model):
    id_tipo_situacion = models.ForeignKey(Tipo_Situacion, null=True, on_delete=models.SET_NULL)
    id_terminal = models.ForeignKey(Terminal, null=True, on_delete=models.SET_NULL)
    fecha = models.DateField(null=False, default=now)
    def __str__(self):
        if self.id_tipo_situacion and self.id_terminal and self.id_terminal.id_titular:
            return self.id_tipo_situacion.nombre+" - "+self.id_terminal.numero_terminal+" - "+self.id_terminal.id_titular.id_persona.nombre + " - "+str(self.fecha)
        elif self.id_tipo_situacion and self.id_terminal:
            return self.id_tipo_situacion.nombre+" - "+self.id_terminal.numero_terminal+ " - "+str(self.fecha)
        elif self.id_tipo_situacion:
            return self.id_tipo_situacion.nombre+ " - "+str(self.fecha)
        elif self.id_terminal and self.id_terminal.id_titular:
            return self.id_terminal.numero_terminal+" - "+self.id_terminal.id_titular.id_persona.nombre+ " - "+str(self.fecha)
        elif self.id_terminal:
            return self.id_terminal.numero_terminal+ " - "+str(self.fecha)

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
    id_tecnologia = models.ForeignKey(Tecnologia, null=True, on_delete=models.SET_NULL, related_name='tecnologias')
    def __str__(self):
        return self.id_desarrollador.nombre+ " - "+self.id_tecnologia.nombre


