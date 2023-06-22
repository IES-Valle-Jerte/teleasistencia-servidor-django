"""
Utilidades para colorear textos en terminal.
author: Aser Granado <github @ ash-dvlpr>

Permiten pandar mensajes colorizados por la terminal.

Los caracteres que sigan a un codigo de escape, seguirán todos ese formato hasta que re haga un RESET.

Para importar en cualquier APP:
    from utilidad.logging import *
        o
    from utilidad.logging import log, red, green, yellow, blue, magenta, cyan
"""


# ANSI ESCAPE CODES
# Color de texto
FG_BLACK = "\033[30m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"
# Color de fondo
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
# Otros
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
NEGATIVE_TEXT = "\003[7m"
POSITIVE_TEXT = "\003[27m"


def _build_tag(tag, ansi_color):
    """
    Contruye una etiqueta rodeandolo con corchetes e insertando los codigos ANSI correspondientes.

    Parameters
    ----------
    tag: str
        Texto para la etiqueta.
    ansi_color: str, optional
        Secuencia de escape ANSI de colores y efectos a aplicar al texto de la etiqueta.

    Returns
    -------
    str
        Etiqueta resultante con formato `[tag]`

    """
    if ansi_color is not None:
        return f"[%s%s%s]" % (ansi_color, tag, RESET)
    else:
        return f"[%s]" % tag


def log(tag, msg, ansi_color=None):
    """
    Hace print() de un mensaje con el siguiente formato:
        `[tag]: msg`
    La etiqueta se puede customizar con secuencias de escape ANSI.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    ansi_color: str, optional
        Secuencia de escape ANSI de colores y efectos a aplicar al texto de la etiqueta del mensaje.
    """
    print(f"%s: %s" % (_build_tag(tag, ansi_color), msg))


def ok(msg):
    green("OK", msg)


def info(msg):
    log("INFO", msg, None)


def warn(msg):
    yellow("WARN", msg)


def error(msg):
    red("ERROR", msg)


def red(tag, msg):
    """
    Realiza un log() de un mensaje la etiqueta roja.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    """
    log(tag, msg, FG_RED)


def green(tag, msg):
    """
    Realiza un log() de un mensaje la etiqueta verde.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    """
    log(tag, msg, FG_GREEN)


def yellow(tag, msg):
    """
    Realiza un log() de un mensaje la etiqueta amarilla.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    """
    log(tag, msg, FG_YELLOW)


def blue(tag, msg):
    """
    Realiza un log() de un mensaje la etiqueta azul.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    """
    log(tag, msg, FG_BLUE)


def magenta(tag, msg):
    """
    Realiza un log() de un mensaje la etiqueta magenta.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    """
    log(tag, msg, FG_MAGENTA)


def cyan(tag, msg):
    """
    Realiza un log() de un mensaje la etiqueta cyan.

    Parameters
    ----------
    tag: str
        Etiqueta del LOG
    msg: str
        Mensaje del LOG
    """
    log(tag, msg, FG_CYAN)

