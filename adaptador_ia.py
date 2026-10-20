"""Selector de proveedores de IA de la Fábrica de Asistentes IA.

Agregar un proveedor nuevo implica crear su adaptador y registrarlo aquí,
sin cambiar el cerebro ni los asistentes ya generados.
"""

import os

from adaptador_cloudflare import (
    CloudflareNoDisponible,
    generar_respuesta_cloudflare,
)
from adaptador_gemini import (
    GeminiNoDisponible,
    generar_respuesta_gemini,
)
from adaptador_ollama import (
    OllamaNoDisponible,
    generar_respuesta_ollama,
)


class ProveedorIANoDisponible(Exception):
    """Indica que el proveedor de IA elegido no pudo responder."""


def obtener_configuracion_ia(configuracion):
    """Obtiene proveedor y modelo, con sobreescritura opcional por entorno."""

    datos = configuracion.get("configuracion_ia", {})
    proveedor = str(datos.get("proveedor", "")).strip().lower()
    modelo = str(datos.get("modelo", "")).strip()

    # Permite probar otra nube sin editar el ADN de cada asistente.
    proveedor = os.getenv("IA_PROVEEDOR", proveedor).strip().lower()
    modelo = os.getenv("IA_MODELO", modelo).strip()

    if not proveedor and modelo.lower().startswith("ollama_local:"):
        proveedor = "ollama_local"
        modelo = modelo.split(":", 1)[1].strip()

    if proveedor == "ollama_local" and modelo.lower().startswith("ollama_local:"):
        modelo = modelo.split(":", 1)[1].strip()

    return {
        "proveedor": proveedor,
        "modelo": modelo,
    }


def proveedor_ia_configurado(configuracion):
    return bool(obtener_configuracion_ia(configuracion)["proveedor"])


def generar_respuesta_ia(mensajes, configuracion):
    """Enruta mensajes al proveedor configurado y devuelve texto y tipo."""

    datos = obtener_configuracion_ia(configuracion)
    proveedor = datos["proveedor"]
    modelo = datos["modelo"] or None

    try:
        if proveedor == "ollama_local":
            return {
                "texto": generar_respuesta_ollama(mensajes, modelo=modelo),
                "tipo": "OLLAMA_LOCAL",
            }

        if proveedor == "cloudflare_workers_ai":
            return {
                "texto": generar_respuesta_cloudflare(mensajes, modelo=modelo),
                "tipo": "CLOUDFLARE_WORKERS_AI",
            }

        if proveedor == "gemini_api":
            return {
                "texto": generar_respuesta_gemini(mensajes, modelo=modelo),
                "tipo": "GEMINI_API",
            }
    except (
        OllamaNoDisponible,
        CloudflareNoDisponible,
        GeminiNoDisponible,
    ) as error:
        raise ProveedorIANoDisponible(str(error)) from error

    raise ProveedorIANoDisponible(
        f"Proveedor de IA no soportado: {proveedor or 'no configurado'}."
    )
