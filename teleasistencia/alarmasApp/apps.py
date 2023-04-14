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

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        # Atributos adicionales
        self.parada_scheduler = None # threading.Event que nos permitirá parar el hilo

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
            self.parada_scheduler = run_scheduler(49) # Realentizamos el scheduler
            # Registramos el evento para que cuando django se esté cerrando, se pare el scheduler
            # TODO

        # Este try-catch es para evitar que se procesen las alarmas cuando la app se inicia para gestionar migraciones
        except Exception:
            # Paramos el hilo
            if self.parada_scheduler is not None:
                self.parada_scheduler.set()


def run_scheduler(intervalo=1):
    """
        Ejecuta en un hilo separado un bucle que mantiene ejecutando el scheduler,
        cada `intervalo` comprobará si hay tareas pendientes (metodos marcados con @repeat).

        NOTA: El intervalo deberá ser igual o inferior al tiempo de repetición de la tarea más rápida.
        Si tenemos una tarea que se ejecuta cada segundo, este deberá ser de 1.

        @param intervalo: tiempo en segundos
        @return cease_continuous_run: threading.Event con el que podremos parar el hilo.
    """
    parar_scheduler = threading.Event()

    # Clase del hilo que ejecutará el scheduler
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not parar_scheduler.is_set():
                schedule.run_pending()
                time.sleep(intervalo)

    # Creamos el hilo
    continuous_thread = ScheduleThread(daemon=True)
    continuous_thread.start()
    # Devolvemos el evento con el que podemos parar el scheduler
    return parar_scheduler


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