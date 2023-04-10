from schedule import repeat, every
import schedule
import threading
import time

from django.apps import AppConfig, apps
from django.db.models import Q
from django.utils.timezone import now

class AlarmasAppConfig(AppConfig):
    """
    Documentación django signals: https://docs.djangoproject.com/en/3.2/topics/signals/
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarmasApp'

    def ready(self):
        """
            Al iniciar la APP, gestionar los eventos de la BBDD.
            
            Las alarmas que puedan estar pendientes (que ya deberían haber sido disparadas)
            las dispara, y el resto las programa para que sean lanzadas cuando llegue su momento
        """
        # ============= Cargar Alarmas Programadas =============
        try:
            procesar_alarmas_programadas()
            print("[\033[33m%s\033[0m]: Procesadas alarmas pendientes" % ('AlarmasApp'))
            # Iniciamos el sheduler para que gestione la tarea de las alarmas programadas
            self.run_scheduler()

        # Este try-catch es para evitar que se procesen las alarmas cuando la app se inicia para gestionar migraciones
        except Exception: pass



    def run_scheduler(self):
        """
            Ejecuta en un hilo separado un bucle que mantiene ejecutando el scheduler
        """
        hilo_tareas = threading.Thread(target=scheduler)
        hilo_tareas.start()


@repeat(every(1).minute)
def procesar_alarmas_programadas():
    """
        Procesa todas las Alarma_Programadas culla fecha de registro sea <= now()
    """
    # Hacemos esto porque no podemos importarlos antes de que django cargue y ejecute las apps
    modelo_alarmas = apps.get_model('teleasistenciaApp', 'Alarma_Programada')

    # Query para identificar si una alarma está pendiente o todavía no se tiene que lanzar
    query_pendientes = Q(fecha_registro__lte=now())
    pendientes = modelo_alarmas.objects.filter(query_pendientes)
    for alarma in pendientes:
        alarma.disparar()


def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10) # Realentizo el bucle manualmente para ahorrar recursos