import time

from django.apps import AppConfig, apps
from django.db.models import Q
from django.utils.timezone import now

import schedule
from schedule import repeat, every
import threading

from utilidad.logging import info, red, green


class SchedulerAppConfig(AppConfig):
    """
    Documentación django signals: https://docs.djangoproject.com/en/3.2/topics/signals/
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedulerApp'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        # Atributos adicionales
        self.scheduler_thread = None  # threading.Thread que ejecuta el scheduler
        self.parada_scheduler = None  # threading.Event que nos permitirá parar el hilo

    def ready(self):
        """
        Al iniciar la APP, gestionar los eventos de la BBDD.

        Las alarmas que puedan estar pendientes (que ya deberían haber sido disparadas)
        las dispara, y el resto las programa para que sean lanzadas cuando llegue su momento
        """
        # ============= Cargar Alarmas Programadas =============
        try:
            procesar_alarmas_programadas()
            green("SchedulerApp", "Procesadas alarmas pendientes")

            # Iniciamos el sheduler para que gestione la tarea de las alarmas programadas
            self.parada_scheduler = self.run_scheduler(10)  # Realentizamos el scheduler un poco
            # Registramos el evento para que cuando django se esté cerrando, se pare el scheduler
            from teleasistencia import shutdown_signal
            shutdown_signal.connect(self.stop_scheduler, sender='system')

        # Este try-catch es para evitar que se procesen las alarmas cuando la app se inicia para gestionar migraciones
        except Exception as e:
            info(e)
            self.stop_scheduler()  # Paramos el hilo

    def run_scheduler(self, intervalo=1):
        """
        Ejecuta en un hilo separado un bucle que mantiene ejecutando el scheduler,
        cada `intervalo` comprobará si hay tareas pendientes (metodos marcados con @repeat).

        Parameters
        ----------
        intervalo: int, optional
            Tiempo en segundos

        Returns
        -------
        parar_scheduler: threading.Event
            Evento que al ser activado con set(), detendrá el bucle del scheduler_thread

        """

        # Devolvemos el evento con el que podemos parar el scheduler
        parar_scheduler = threading.Event()

        # Clase del hilo que ejecutará el scheduler
        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not parar_scheduler.is_set():
                    schedule.run_pending()
                    time.sleep(intervalo)

        # Creamos el hilo
        self.scheduler_thread = ScheduleThread(daemon=True)
        self.scheduler_thread.start()

        return parar_scheduler

    def stop_scheduler(self, **kwargs):
        if self.parada_scheduler is not None:
            self.parada_scheduler.set()
            self.scheduler_thread.join()
            red("SchedulerApp", "Scheduler Detenido")


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
