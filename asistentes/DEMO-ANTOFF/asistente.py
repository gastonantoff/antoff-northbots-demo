import os
import sys


RUTA_ASISTENTE = os.path.dirname(
    os.path.abspath(__file__)
)

RUTA_PROYECTO = os.path.dirname(
    os.path.dirname(RUTA_ASISTENTE)
)

if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)

from runtime_asistente import ejecutar_asistente


def ejecutar(mensaje, contexto=None):
    """Punto de entrada del asistente demo."""

    return ejecutar_asistente(
        mensaje=mensaje,
        contexto=contexto,
        configuracion=os.path.join(
            RUTA_ASISTENTE,
            "configuracion.json"
        ),
        cerebro=os.path.join(
            RUTA_ASISTENTE,
            "cerebro.json"
        ),
        personalidad=os.path.join(
            RUTA_ASISTENTE,
            "personalidad.json"
        ),
    )