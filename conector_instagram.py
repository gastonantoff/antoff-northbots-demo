"""Funciones base del conector real de Instagram.

No guarda secretos ni realiza envíos automáticos.
La conexión con Meta se activará sólo después de configurar el webhook HTTPS.
"""

import hashlib
import hmac

from configuracion_instagram import (
    configuracion_instagram_lista,
    obtener_configuracion_instagram,
    obtener_faltantes_instagram,
)


def obtener_estado_conector():
    """Devuelve el estado de preparación sin exponer datos sensibles."""
    configuracion = obtener_configuracion_instagram()

    return {
        "canal": "instagram",
        "estado": (
            "LISTO_PARA_CONFIGURAR_WEBHOOK"
            if configuracion_instagram_lista(configuracion)
            else "CONFIGURACION_PENDIENTE"
        ),
        "variables_faltantes": obtener_faltantes_instagram(configuracion),
    }


def verificar_token_webhook(token_recibido):
    """Valida el token enviado por Meta durante el alta del webhook."""
    configuracion = obtener_configuracion_instagram()

    token_esperado = configuracion["verify_token"].strip()
    token_recibido = (token_recibido or "").strip()

    if not token_esperado or not token_recibido:
        return False

    return hmac.compare_digest(token_recibido, token_esperado)


def verificar_firma_evento(cuerpo, firma_recibida):
    """Comprueba que el evento fue firmado por Meta."""
    configuracion = obtener_configuracion_instagram()
    secreto = configuracion["app_secret"]

    if not secreto or not firma_recibida:
        return False

    firma_esperada = "sha256=" + hmac.new(
        secreto.encode("utf-8"),
        cuerpo,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(firma_esperada, firma_recibida)


def procesar_evento_instagram(evento):
    """Valida la estructura mínima de un evento recibido desde Meta.

    Por ahora no envía respuestas ni llama APIs externas.
    """
    if not isinstance(evento, dict):
        return {
            "aceptado": False,
            "motivo": "El evento debe ser un objeto JSON.",
        }

    entradas = evento.get("entry", [])

    if not isinstance(entradas, list):
        return {
            "aceptado": False,
            "motivo": "El campo 'entry' debe ser una lista.",
        }

    return {
        "aceptado": True,
        "cantidad_entradas": len(entradas),
    }


from pathlib import Path
import importlib.util
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from motor_contexto import crear_contexto


CONTEXTOS_INSTAGRAM = {}


def extraer_mensajes_instagram(evento):
    """Extrae mensajes de texto recibidos desde el webhook."""
    mensajes = []

    for entrada in evento.get("entry", []):
        for elemento in entrada.get("messaging", []):
            mensaje = elemento.get("message", {})

            if mensaje.get("is_echo"):
                continue

            texto = mensaje.get("text", "").strip()
            remitente = elemento.get("sender", {}).get("id")

            if texto and remitente:
                mensajes.append({
                    "remitente_id": str(remitente),
                    "texto": texto,
                })

    return mensajes


def responder_con_asistente_instagram(remitente_id, texto):
    """Ejecuta el asistente fabricado para una conversación de Instagram."""
    ruta_proyecto = Path(__file__).resolve().parent
    ruta_asistente = (
        ruta_proyecto
        / "asistentes"
        / "AST-000001"
        / "asistente.py"
    )

    if not ruta_asistente.is_file():
        return "El asistente todavía no está disponible."

    especificacion = importlib.util.spec_from_file_location(
        "asistente_instagram",
        ruta_asistente,
    )

    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)

    contexto = CONTEXTOS_INSTAGRAM.get(remitente_id)

    if contexto is None:
        contexto = crear_contexto()
        CONTEXTOS_INSTAGRAM[remitente_id] = contexto

    resultado = modulo.ejecutar(
        mensaje=texto,
        contexto=contexto,
    )

    respuesta = resultado.get("respuesta", {}).get("texto", "").strip()

    return respuesta or "No pude generar una respuesta en este momento."


def enviar_mensaje_instagram(destinatario_id, texto):
    """Envía una respuesta de texto mediante la API de Instagram."""
    configuracion = obtener_configuracion_instagram()

    token = configuracion["access_token"]
    cuenta_id = configuracion["ig_user_id"]
    version = configuracion["graph_api_version"] or "v24.0"

    if not token or not cuenta_id:
        return {"enviado": False, "motivo": "CONFIGURACION_INCOMPLETA"}

    url = (
        f"https://graph.instagram.com/"
        f"{version}/{cuenta_id}/messages"
    )

    cuerpo = json.dumps({
        "recipient": {"id": destinatario_id},
        "message": {"text": texto},
    }).encode("utf-8")

    solicitud = Request(
        url,
        data=cuerpo,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(solicitud, timeout=15) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))

        return {
            "enviado": True,
            "mensaje_id": datos.get("message_id"),
        }

    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return {
            "enviado": False,
            "motivo": "ERROR_ENVIO_INSTAGRAM",
        }