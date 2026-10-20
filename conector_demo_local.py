"""
Conector del asistente demo local.

Mantiene el contexto de cada conversación y ejecuta el
asistente DEMO-ANTOFF sin exponerlo todavía a Internet.
"""

import importlib.util
from pathlib import Path

from motor_contexto import crear_contexto


CONTEXTOS_DEMO = {}


def cargar_asistente_local(asistente_id):
    ruta_proyecto = Path(__file__).resolve().parent

    asistente_id = str(asistente_id or "").strip()

    if not asistente_id or Path(asistente_id).name != asistente_id:
        raise ValueError("Identificador de asistente local inválido.")

    ruta_asistente = (
        ruta_proyecto
        / "asistentes"
        / asistente_id
        / "asistente.py"
    )

    if not ruta_asistente.is_file():
        raise FileNotFoundError(
            "No se encontró el asistente local solicitado."
        )

    especificacion = importlib.util.spec_from_file_location(
        f"asistente_local_{asistente_id.replace('-', '_')}",
        ruta_asistente,
    )

    modulo = importlib.util.module_from_spec(
        especificacion
    )

    especificacion.loader.exec_module(modulo)

    return modulo


def responder_asistente_local(
    asistente_id,
    conversacion_id,
    texto,
):
    if not texto or not str(texto).strip():
        return {
            "estado": "MENSAJE_VACIO",
            "exito": False,
            "respuesta": (
                "Necesito un mensaje para poder responder."
            ),
        }

    asistente_id = str(asistente_id).strip()
    conversacion_id = str(conversacion_id or "demo_local")
    clave_contexto = f"{asistente_id}:{conversacion_id}"

    contexto = CONTEXTOS_DEMO.get(clave_contexto)

    if contexto is None:
        contexto = crear_contexto()
        CONTEXTOS_DEMO[clave_contexto] = contexto

    asistente = cargar_asistente_local(asistente_id)

    resultado = asistente.ejecutar(
        mensaje=str(texto).strip(),
        contexto=contexto,
    )

    respuesta = resultado.get(
        "respuesta",
        {}
    ).get(
        "texto",
        ""
    ).strip()

    return {
        "estado": resultado.get(
            "estado",
            "SIN_ESTADO",
        ),
        "exito": resultado.get(
            "exito",
            False,
        ),
        "respuesta": (
            respuesta
            or "No pude generar una respuesta ahora."
        ),
    }


def cargar_asistente_demo():
    """Compatibilidad con la demo institucional existente."""
    return cargar_asistente_local("DEMO-ANTOFF")


def responder_demo(conversacion_id, texto):
    """Compatibilidad con la demo institucional existente."""
    return responder_asistente_local(
        "DEMO-ANTOFF",
        conversacion_id,
        texto,
    )
