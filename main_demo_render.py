"""Aplicación pública mínima para la demo de Lumen Moda en Render.

Mantiene las pantallas de administración de la fábrica fuera del servicio
expuesto a Internet. La aplicación principal sigue siendo ``main.py`` para
el trabajo local.
"""

import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from conector_demo_local import responder_asistente_local


app = FastAPI(title="ANT0FF Northbots · Demo")

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


@app.get("/", include_in_schema=False)
def inicio():
    """Envía el enlace principal a la demo comercial."""
    return RedirectResponse(url="/demo/lumen-moda")


@app.get("/salud")
def salud():
    """Comprobación mínima para el alojamiento."""
    return {"estado": "ok"}


@app.get("/demo/lumen-moda")
def ver_demo_lumen_moda(request: Request):
    """Muestra la única página pública del servicio."""
    return templates.TemplateResponse(
        request=request,
        name="demo_chat.html",
        context={
            "titulo_demo": "Lumen Moda · Demo",
            "subtitulo_demo": "Asistente comercial ficticio de prueba",
            "saludo_demo": (
                "¡Hola! Soy Lumi, la asesora digital de Lumen Moda. "
                "Podés consultarme por productos, precios, talles o envíos. "
                "Si probás una compra, usá datos ficticios: esta demo no "
                "registra pedidos reales."
            ),
            "endpoint_chat": "/demo/lumen-moda/chat",
            "clave_conversacion": "lumen_moda_demo_conversacion",
        },
    )


@app.post("/demo/lumen-moda/chat")
async def conversar_con_lumen_moda(request: Request):
    """Genera una respuesta de la demo para quien visite el enlace público."""
    try:
        datos = await request.json()
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="El cuerpo debe ser un objeto JSON válido.",
        ) from error

    if not isinstance(datos, dict):
        raise HTTPException(
            status_code=422,
            detail="El cuerpo debe ser un objeto JSON.",
        )

    try:
        resultado = responder_asistente_local(
            "AST-000002",
            datos.get("conversacion_id"),
            datos.get("mensaje", ""),
        )
    except Exception:
        # No se exponen detalles internos ni claves en una URL pública.
        raise HTTPException(
            status_code=503,
            detail="La demo no está disponible temporalmente.",
        ) from None

    return JSONResponse(content=resultado)
