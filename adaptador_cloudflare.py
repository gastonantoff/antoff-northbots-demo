"""Proveedor remoto Cloudflare Workers AI para la Fábrica de Asistentes IA.

Las credenciales se toman únicamente de variables de entorno. Nunca deben
guardarse en configuraciones de asistentes, la base de datos ni el repositorio.
"""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


MODELO_PREDETERMINADO = "@cf/meta/llama-3.1-8b-instruct"


class CloudflareNoDisponible(Exception):
    """Indica que Workers AI no pudo generar una respuesta."""


def generar_respuesta_cloudflare(mensajes, modelo=None, timeout=45):
    """Genera texto usando la API REST de Workers AI.

    Requiere las variables CLOUDFLARE_ACCOUNT_ID y
    CLOUDFLARE_WORKERS_AI_TOKEN en el entorno del servidor.
    """

    if not isinstance(mensajes, list) or not mensajes:
        raise ValueError("Se requiere al menos un mensaje para Cloudflare.")

    cuenta = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.getenv("CLOUDFLARE_WORKERS_AI_TOKEN", "").strip()

    if not cuenta or not token:
        raise CloudflareNoDisponible(
            "Faltan CLOUDFLARE_ACCOUNT_ID o CLOUDFLARE_WORKERS_AI_TOKEN."
        )

    nombre_modelo = (modelo or MODELO_PREDETERMINADO).strip()
    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{cuenta}/ai/run/{quote(nombre_modelo, safe='@/') }"
    )

    cuerpo = json.dumps(
        {
            "messages": mensajes,
            "max_tokens": 220,
            "temperature": 0.3,
        }
    ).encode("utf-8")

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
        with urlopen(solicitud, timeout=timeout) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as error:
        raise CloudflareNoDisponible(
            "No se pudo conectar con Cloudflare Workers AI."
        ) from error
    except json.JSONDecodeError as error:
        raise CloudflareNoDisponible(
            "Cloudflare devolvió una respuesta inválida."
        ) from error

    if not datos.get("success", False):
        errores = datos.get("errors", [])
        detalle = errores[0].get("message", "Error de Cloudflare.") if errores else "Error de Cloudflare."
        raise CloudflareNoDisponible(detalle)

    texto = str(datos.get("result", {}).get("response", "")).strip()

    if not texto:
        raise CloudflareNoDisponible("Cloudflare no generó una respuesta.")

    return texto
