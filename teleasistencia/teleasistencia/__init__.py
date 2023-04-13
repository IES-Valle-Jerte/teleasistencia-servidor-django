import signal
import sys
from django import dispatch

# Django Signal custom para parar notificar a diversos procesos
shutdown_signal = dispatch.Signal()

def shutdown_handler(*args):
    # Para que funcione es CRUCIAL que ejecutemos el servidor con --noreload
    print("[\033[33mDETENIENDO SERVIDOR\033[0m]: Deteniendo hilos...")
    shutdown_signal.send(sender='system')
    sys.exit(0)


# Registrar evento a ejecutar cuando se intente parar el servidor
signal.signal(signal.SIGINT, shutdown_handler)   # Parado con Ctrl+C
signal.signal(signal.SIGTERM, shutdown_handler)  # Parado con process kill
