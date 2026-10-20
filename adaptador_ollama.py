"""
Proveedor local de lenguaje para la Fábrica de Asistentes IA.

Usa Ollama en la propia computadora. No requiere API key,
no envía mensajes a servicios externos y no ejecuta acciones.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL_OLLAMA = "http://127.0.0.1:11434/api/chat"
MODELO_PREDETERMINADO = "qwen3:1.7b"


class OllamaNoDisponible(Exception):
    """Indica que el servicio local de Ollama no está disponible."""

def cerrar_respuesta(texto):
    texto = texto.strip()

    if texto.endswith((".", "!", "?")):
        return texto

    posiciones = [
        texto.rfind("."),
        texto.rfind("!"),
        texto.rfind("?"),
    ]

    ultimo_cierre = max(posiciones)

    if ultimo_cierre >= 0:
        texto = texto[:ultimo_cierre + 1].strip()

    if not texto:
        texto = "Puedo orientarte sobre asistentes digitales para negocios."

    return (
        f"{texto}\n\n"
        "¿Querés que conversemos sobre tu negocio?"
    )


def generar_respuesta_ollama(
    mensajes,
    modelo=MODELO_PREDETERMINADO,
    timeout=180,
):
    """
    Genera una respuesta local a partir de mensajes con formato:
    {"role": "system|user|assistant", "content": "..."}.
    """

    if not isinstance(mensajes, list) or not mensajes:
        raise ValueError("Se requiere al menos un mensaje para Ollama.")

    cuerpo = json.dumps(
        {
            "model": modelo,
            "messages": mensajes,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 220,
            },
        }
    ).encode("utf-8")

    solicitud = Request(
        URL_OLLAMA,
        data=cuerpo,
        method="POST",
        headers={
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(solicitud, timeout=timeout) as respuesta:
            datos = json.loads(
                respuesta.read().decode("utf-8")
            )
    except (HTTPError, URLError, TimeoutError) as error:
        raise OllamaNoDisponible(
            "No se pudo conectar con Ollama local."
        ) from error
    except json.JSONDecodeError as error:
        raise OllamaNoDisponible(
            "Ollama devolvió una respuesta inválida."
        ) from error

    texto = (
        datos.get("message", {})
        .get("content", "")
        .strip()
    )

    if not texto:
        raise OllamaNoDisponible(
            "Ollama no generó una respuesta."
        )

    return cerrar_respuesta(texto)