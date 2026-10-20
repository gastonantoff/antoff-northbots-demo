"""Proveedor Gemini API para la Fábrica de Asistentes IA.

La clave se lee únicamente de GEMINI_API_KEY en el entorno del servidor.
Nunca debe guardarse en JSON, SQLite ni en el repositorio.
"""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


MODELO_PREDETERMINADO = "gemini-2.5-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiNoDisponible(Exception):
    """Indica que Gemini no pudo generar una respuesta."""


def _convertir_mensajes(mensajes):
    """Convierte los roles internos al formato REST de Gemini."""

    sistema = []
    contenidos = []

    for mensaje in mensajes:
        rol = mensaje.get("role")
        texto = str(mensaje.get("content", "")).strip()

        if not texto:
            continue

        if rol == "system":
            sistema.append(texto)
            continue

        contenidos.append(
            {
                "role": "model" if rol == "assistant" else "user",
                "parts": [{"text": texto}],
            }
        )

    if not contenidos:
        raise ValueError("Se requiere un mensaje de usuario para Gemini.")

    cuerpo = {
        "contents": contenidos,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 220,
        },
    }

    if sistema:
        cuerpo["systemInstruction"] = {
            "parts": [{"text": "\n".join(sistema)}],
        }

    return cuerpo


def generar_respuesta_gemini(mensajes, modelo=None, timeout=45):
    """Genera una respuesta mediante Gemini REST API."""

    clave = os.getenv("GEMINI_API_KEY", "").strip()

    if not clave:
        raise GeminiNoDisponible("Falta configurar GEMINI_API_KEY.")

    nombre_modelo = (modelo or MODELO_PREDETERMINADO).strip()
    url = f"{URL_BASE}/{quote(nombre_modelo, safe='-._')}:generateContent"

    solicitud = Request(
        url,
        data=json.dumps(_convertir_mensajes(mensajes)).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": clave,
        },
    )

    try:
        with urlopen(solicitud, timeout=timeout) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except HTTPError as error:
        raise GeminiNoDisponible(
            f"Gemini rechazó la solicitud (HTTP {error.code})."
        ) from error
    except (URLError, TimeoutError) as error:
        raise GeminiNoDisponible(
            "No se pudo conectar con Gemini."
        ) from error
    except json.JSONDecodeError as error:
        raise GeminiNoDisponible(
            "Gemini devolvió una respuesta inválida."
        ) from error

    candidatos = datos.get("candidates", [])
    partes = (
        candidatos[0].get("content", {}).get("parts", [])
        if candidatos else []
    )
    texto = "".join(
        str(parte.get("text", ""))
        for parte in partes
    ).strip()

    if not texto:
        raise GeminiNoDisponible("Gemini no generó una respuesta.")

    return texto
