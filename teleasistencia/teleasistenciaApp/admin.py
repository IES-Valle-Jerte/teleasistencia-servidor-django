import fileinput

from django.contrib import admin

from pathlib import Path
from .models import *

# Register your models here.

admin.site.register(Logs_AccionesUsuarios)
admin.site.register(Logs_ConexionesUsuarios)
admin.site.register(Imagen_User)
admin.site.register(Tipo_Agenda)
admin.site.register(Direccion)
admin.site.register(Clasificacion_Alarma)
admin.site.register(Tipo_Alarma)
admin.site.register(Clasificacion_Recurso_Comunitario)
admin.site.register(Tipo_Recurso_Comunitario)
admin.site.register(Recurso_Comunitario)
admin.site.register(Persona)
admin.site.register(Tipo_Modalidad_Paciente)
admin.site.register(Paciente)
admin.site.register(Relacion_Paciente_Persona)
admin.site.register(Tipo_Vivienda)
admin.site.register(Terminal)
admin.site.register(Relacion_Terminal_Recurso_Comunitario)
admin.site.register(Agenda)
admin.site.register(Historico_Agenda_Llamadas)
admin.site.register(Dispositivos_Auxiliares_En_Terminal )
admin.site.register(Alarma)
admin.site.register(Alarma_Programada)
admin.site.register(Persona_Contacto_En_Alarma)
admin.site.register(Recursos_Comunitarios_En_Alarma)
admin.site.register(Tipo_Situacion)
admin.site.register(Desarrollador)
admin.site.register(Tecnologia)
admin.site.register(Desarrollador_Tecnologia)
admin.site.register(Convocatoria_Proyecto)
admin.site.register(Database_User)


class Database_form_admin(admin.ModelAdmin):

    # Actualiza los datos de conexión de la base de datos
    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)
        self.updateEnvDatabase()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self.updateEnvDatabase()
    def delete_queryset(self, request, obj):
        super().delete_queryset(request, obj)
        self.updateEnvDatabase()

    # Actualiza la constante DATABASES del archivo .env relativa a la base de datos
    def updateEnvDatabase(self):

        databases = Database.objects.all()
        jsonDatabase = {}
        for database in databases:
            if "sqlite" in database.engine:
                jsonDatabase[database.nameDescritive] = {
                    "ENGINE": database.engine,
                    "NAME": database.name
                }
            else:
                jsonDatabase[database.nameDescritive] = {
                    "ENGINE": database.engine,
                    "NAME": database.name,
                    "USER": database.user,
                    "PASSWORD": database.password,
                    "HOST": database.host,
                    "PORT": database.port
                }

            ## TODO Hay que añadir el caso de postgres

        with fileinput.FileInput(str(Path(__file__).resolve().parent.parent)+"\.env", inplace=True) as f:
            for line in f:
                if "DATABASES" in line:
                    print("DATABASES = '" + str(jsonDatabase).replace("'", '"') + "'", end='\n')
                else:
                    print(line, end='')
        print (jsonDatabase)

admin.site.register(Database, Database_form_admin)

